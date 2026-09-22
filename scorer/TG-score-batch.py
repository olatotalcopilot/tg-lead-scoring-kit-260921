#!/usr/bin/env python3
"""TG Sales Agency — batch scorer. Rubric v3.1.

Reusable across runs. The scoring MATH lives here and must not be re-derived by hand;
the per-run HUMAN JUDGEMENT lives in judgments.json. Change the judgements, not this file.

  python3 TG-score-batch.py --config run-config.json

See method/2-run-playbook.md for the pipeline this sits in, and
method/1-scoring-rubric.md for why each weight is what it is. If the rubric and this
file ever disagree, the rubric wins and this file is the bug.

────────────────────────────────────────────────────────────────────────── INPUTS
run-config.json   {campaign, score_date, rubric_version, scoring_mode, paths{...}}
roster.csv        Apollo saved-list export. One row per contact. Required columns:
                  contact_id, person_id, first, last, title, company, domain, website,
                  li_company, li_person, email, email_status, direct_phone,
                  city, state, country, org_id, account_id, created, label_ids, founded
                  NOTE: this is a point-in-time Contact snapshot, not live data.
verified.csv      Output of the mandatory Apollo people-match pass. Required columns:
                  contact_id, person_id, new_title, new_company, domain, emp, rev,
                  industry, country, email, email_status, seniority, hq_country
matched.json      RAW people_match responses keyed by person_id, employment_history
                  intact. Used for the snapshot-vs-live departure test — see
                  _open_ended_at(). A flattened or contact_id-keyed file cannot answer
                  that question and the run stops rather than guessing.
offshore.json     {domain: {num, den, pct, verdict}}  verdict ∈ PASS|REVIEW|DISQUALIFY
research.txt      One pipe-delimited line per domain, 19 fields:
                  domain|acq|acq_detail|distress|competitor|hiring|web|ticket|growth|
                  messy|followers|posts|range|median|li_mkt|li_growth|li_hire|note|urls
li-urls.json      {domain: {url, source}} company LinkedIn pages, captured at lookup
                  time. Optional; absent means li_company ships empty, which is not
                  evidence that a company has no page.
judgments.json    Per-run human calls. Every key optional; see JUDGEMENT_KEYS below.

───────────────────────────────────────────────────────────────────────── OUTPUT
TG-scored-full-<campaign>-<rubric_version>.csv — one row per contact, schema per
method/3-field-schema.md. Ready for CRM export.

Two prose columns, with strictly separate jobs — keep them separate:
  verdict         judgement and action. Why this row is where it is, the question a
                  reviewer must answer, and what to do next.
  record_caveats  provenance only. What we CHANGED about this record, or what we do
                  not TRUST in it. Nothing derivable from another column belongs here —
                  "no email on file" restates email_status, "no Layer 3" restates the
                  layer3 columns. Blank is the normal case (~86% of rows).
"""
import csv, json, collections, re, sys, argparse, os

# Kit and rubric share one version line: major.minor.patch.
#   major  the model changes shape — a new layer or score; everything needs rescoring
#   minor  anything that CAN change a number, a tier, a route or a column on some row
#   patch  nothing about any scored output can change — documents, packaging, or a guard
#          that only refuses malformed input
# Only major.minor reaches the data. `rubric_version` is a comparability key stamped on
# every row, so equality on it has to mean "these rows are comparable"; letting a patch
# bump through would split one comparable population in two for no reason.
KIT_VERSION      = '3.1.1'
RUBRIC_SUPPORTED = 'v3.1'

JUDGEMENT_KEYS = {
    'parent_control_confirmed': 'domain -> reason. Operational evidence the parent runs hiring/'
                        'procurement/web presence. Disqualifies at ANY deal age.',
    'parent_control_inferred':  'domain -> reason. Branding evidence only ("X, an Acme company"). '
                        'Routes to Review if otherwise Qualified+, else disqualifies.',
    'serial_acquirer':  'domain -> reason. Decentralised permanent holders (Constellation/'
                        'Volaris, Valsoft). Scored normally, like a financial sponsor.',
    'pe_recent':        'domain -> reason. Financial sponsor, recap within ~18 months -> Review.',
    'pe_backed':        'domain -> reason. Financial sponsor, older. Scored normally; '
                        'recorded in `ownership` only.',
    'distress':         'domain -> reason. Hard disqualifier.',
    'competitor':       'domain -> reason. Hard disqualifier.',
    'b2c':              'domain -> reason. Heavy score penalty, NOT a disqualifier.',
    'left':             'contact_id -> note. Contact has left; curated detail beats the '
                        'generic snapshot message.',
    'unverifiable':     'contact_id -> note. The person cannot be placed at this company by any key '
                        '(identifier, LinkedIn URL, email, name-at-domain). Distinct from `left`: they '
                        'were never there, rather than having moved on.',
    'mismatch_review':  'contact_id -> note. List/Apollo/web disagree on employer.',
    'name_fix':         'domain -> corrected company name (Apollo org names are unreliable).',
    'domain_confirmed': 'domain -> who checked and what they found. Clears a '
                        'DOMAIN NOT CORROBORATED flag once a human has verified the '
                        'record domain really is the company (e.g. a legacy mail domain). '
                        'The flag cannot tell an alternate domain from a wrong one — only '
                        'a web check can, so the clearance is recorded here and persists.',
    'ctype_override':   'domain -> int 0-12. Overrides Proven-Fit company_type.',
    'ind_override':     'domain -> int 0-10. Overrides Ideal-Fit industry.',
    'row_overrides':    'contact_id -> {column: value}. Last-resort hand corrections; '
                        'each one should say why in record_caveats.',
}

OFFSHORE_COUNTRIES = ("India, Philippines, Pakistan, Bangladesh, Sri Lanka, "
                      "Vietnam, Indonesia")
# Apollo industry string -> Ideal-Fit industry points. Standing map (rubric-derived,
# not per-run): Primary 10 / Secondary 7 / Additional 5 / off-list sales-motion up to 8.
# Anything unmapped defaults to 8 and should be confirmed or overridden per run.
IND_BY_APOLLO = {'information technology & services':10, 'computer & network security':10,
                 'telecommunications':7, 'information services':10, 'research':8,
                 'e-learning':8, 'insurance':10, 'online media':7}

# Layer 1 geography is scored on the CONTACT's country, never the company HQ. The bands
# are US / Europe-ME / other. "Europe" is read geographically — the rationale is time-zone
# and contracting workability, not EU membership — so the UK and Switzerland are included.
EUROPE_ME = {
    'United Kingdom','Ireland','France','Germany','Spain','Portugal','Italy','Netherlands',
    'Belgium','Luxembourg','Austria','Switzerland','Denmark','Sweden','Norway','Finland',
    'Iceland','Poland','Czechia','Czech Republic','Slovakia','Hungary','Slovenia','Croatia',
    'Romania','Bulgaria','Greece','Estonia','Latvia','Lithuania','Malta','Cyprus','Serbia',
    'Ukraine','United Arab Emirates','Saudi Arabia','Qatar','Kuwait','Bahrain','Oman',
    'Israel','Jordan','Lebanon','Turkey','Egypt',
}
def geo_p(c):  return 3 if c == 'United States' else 2 if c in EUROPE_ME else 0
def geo_i(c):  return 5 if (c == 'United States' or c in EUROPE_ME) else 0

# Layer 2 maps email_status to points by exact string, so an unrecognised value silently
# scores 0 — worth 4 or 8 points on every row carrying it. Anything outside this set stops
# the run. Apollo's `email_true_status = "User Managed"` means the address came from an
# upload rather than Apollo validation: normalise it to `unverified` in verified.csv.
KNOWN_EMAIL_STATUS = {'verified', 'unverified', 'extrapolated', 'likely to engage',
                      'unavailable', ''}

# Free/public mailbox domains never corroborate a company domain.
PUBLIC_MAIL = {'gmail.com','yahoo.com','hotmail.com','outlook.com','aol.com',
               'icloud.com','me.com','msn.com','live.com','protonmail.com'}

# ───────────────────────────────────────────────────────────── scoring primitives
# These implement TG-lead-scoring-rubric.md v3.1 Layer 1. Do not tune here without
# bumping rubric_version — scores are only comparable within a version.

def tier(s):
    if s == '' or s is None: return 'Invalid'
    return "Hot" if s>=80 else "Qualified" if s>=60 else "Nurture" if s>=40 else "Skip"

def size_p(e):
    # A blank employee count scores 0, not the small-company 8: absence of evidence is not
    # evidence of being small, and a row with no firmographics must not outscore a known
    # 120-person company on Size. The rubric has no "unknown" size band, so this scores 0 AND
    # the row is force-routed to Review as firmographics_unavailable — the number is never
    # acted on without a human.
    if not e: return 0
    e = int(float(e))
    return 8 if e<=50 else 6 if e<=100 else 4 if e<=200 else 1

def title_p(t, sen):
    t = (t or '').lower()
    if any(k in t for k in ['chief executive','ceo','founder','owner','co-founder','chairman']): return 12
    if any(k in t for k in ['president','coo','chief operating']): return 9
    if any(k in t for k in ['chief revenue','head of revenue','head of gtm','chief growth']): return 6
    if any(k in t for k in ['vp','vice president','cro','chief sales','chief commercial','svp','head of sales']): return 4
    return 3

def persona_i(t, sen):
    t = (t or '').lower()
    if any(k in t for k in ['chief executive','ceo','founder','owner','co-founder','chairman',
                            'chief revenue','cro','vp of sales','vice president of sales','vp sales']): return 10
    if any(k in t for k in ['head of revenue','head of gtm','chief growth']): return 9
    if any(k in t for k in ['president','coo','chief operating']): return 8
    if any(k in t for k in ['vp','vice president','svp','director','sales','chief','head']): return 4
    return 3

def size_x_title(e, sen):
    e = int(float(e)) if e else 0
    founder = sen in ('c_suite','founder','owner')
    if e<20 or e>1000: return 2 if founder else 0
    if founder: return 8 if e<=200 else 6 if e<=500 else 2
    if sen in ('vp','head'): return 8 if 100<=e<=500 else 4
    return 3

def revenue_i(r):
    r = float(r) if r else 0
    if 10_000_000<=r<=100_000_000: return 7
    if 3_000_000<=r<10_000_000: return 5
    return 3 if r==0 else 0

def deal_p(r):
    r = float(r) if r else 0
    return 5 if r>=1_000_000 else 2

# Company-level rescaling denominators. Company score = every criterion that is a
# property of the COMPANY (so: minus the person-specific ones, minus reachability),
# rescaled to 0-100.
#   Proven: Layer1P 40 - title 12 = 28, + L3A 30 + L3B 15 = 73
#   Ideal:  Layer1I 40 - persona 10 - size_x_title 8 = 22, + L3A 30 + L3B 15 = 67
PC_DIVISOR, IC_DIVISOR = 73, 67

# ────────────────────────────────────────────────────── snapshot vs live (v3.1)
def _norm(s): return re.sub(r'[^a-z0-9]','',(s or '').lower())

def _matched_supports_departure_test(matched, roster):
    """Can matched.json actually answer the departure question?

    It can only do so if it is keyed by the roster's `person_id` AND carries
    `employment_history`. The playbook requires matched.json to hold the RAW
    people_match responses for exactly this reason. A flattened matched.json — keyed
    by contact_id, or with the history dropped — makes _open_ended_at() return False
    for every contact, which reads as "this person has left" rather than "we cannot
    tell". Silent and wrong in the dangerous direction, so it is detected, not assumed.
    """
    if not any((v or {}).get('employment_history') for v in matched.values()):
        return False, 'no entry carries employment_history'
    pids = [r.get('person_id') for r in roster.values() if r.get('person_id')]
    if not pids:
        return False, 'roster has no person_id values to key on'
    if not any(p in matched for p in pids):
        return False, 'matched.json is not keyed by the roster person_id'
    return True, ''

def _open_ended_at(matched, src, usable):
    """True when the live People record still shows an open-ended role at the company
    named in the saved-list snapshot. Matches on company NAME, not Apollo's `current`
    flag, which is unreliable (records exist with end_date null and current false).

    Returns (answer, reason_unanswerable). A False answer is only meaningful when the
    reason is empty; otherwise the question could not be asked and the caller must not
    read the False as "this person left". `usable` is required, not defaulted — a
    default of True would re-arm exactly the bug this exists to prevent.

    The file-level check in _matched_supports_departure_test() is necessary but NOT
    sufficient: a matched.json can satisfy it on one entry and still be missing the
    contact in front of us. So every precondition is re-checked per row.
    """
    if not usable:
        return False, 'matched.json cannot answer the departure question'
    pid = src.get('person_id')
    if not pid:
        return False, 'the roster row carries no person_id to look up'
    p = matched.get(pid)
    if p is None:
        return False, f'person_id {pid} is not present in matched.json'
    if not p.get('employment_history'):
        return False, f'the matched.json entry for {pid} carries no employment_history'
    rc = _norm(src.get('company'))
    if not rc:
        return False, 'the roster row carries no company name to match against'
    for e in p['employment_history']:
        if e.get('end_date'): continue
        on = _norm(e.get('organization_name'))
        if on and (rc in on or on in rc): return True, ''
    return False, ''

def _last_role(matched, src):
    p = matched.get(src.get('person_id')) or {}
    ended = sorted([e for e in (p.get('employment_history') or []) if e.get('end_date')],
                   key=lambda e: e['end_date'], reverse=True)
    return (f"{ended[0].get('organization_name')} (ended {ended[0]['end_date'][:7]})"
            if ended else 'no employment history on record')

def _corroborated(domain, email):
    """Confirming the contact does NOT confirm the domain. Cheapest check is the
    contact's own email domain. Returns (ok, note)."""
    if not domain or not email or '@' not in email: return True, ''
    ed = email.split('@')[-1].strip().lower()
    if ed in PUBLIC_MAIL or ed == domain.lower(): return True, ''
    a, b = _norm(domain.split('.')[0]), _norm(ed.split('.')[0])
    if a and b and (a in b or b in a): return True, ''
    return False, (f'DOMAIN NOT CORROBORATED: record domain {domain} does not match the '
                   f'contact email domain {ed}. Confirm the company before screening or '
                   f'scoring on this domain — a ratio measured for the wrong company '
                   f'looks like evidence.')

def reason_of(review):
    """Map the leading Review trigger to the review_reason enum (rubric v3.1)."""
    if not review: return ''
    s = review[0]
    for prefix, val in (
        ('INDEPENDENT BUYING AUTHORITY UNCONFIRMED','unconfirmed_independent_buying_authority'),
        ('CONTACT LEFT COMPANY','contact_left_company'),
        ('CONTACT UNVERIFIABLE','contact_unverifiable'),
        ('RECENT PE RECAP','pe_recent_recap'),
        ('OFFSHORE','offshore_small_sample'),
        ('EMPLOYER MISMATCH','employer_mismatch'),
        ('OWNERSHIP UNKNOWN','ownership_unknown'),
        ('FIRMOGRAPHICS UNAVAILABLE','firmographics_unavailable'),
    ):
        if s.startswith(prefix): return val
    if s.startswith('No company domain') or s.startswith('Domain not covered'): return 'not_researched'
    # An uncorroborated domain maps to `employer_mismatch`, not `ownership_unknown`: the
    # question is whether the domain is the right company at all, not who owns it. A
    # dedicated `domain_uncorroborated` reason is a roadmap item.
    if s.startswith('DOMAIN NOT CORROBORATED'): return 'employer_mismatch'
    return ''

# ───────────────────────────────────────────────────────────────────────── main
def validate(out):
    """Assert the rubric's invariants against the finished rows. Rules the rubric states
    in prose are only real if something checks them — hand-authored or overridden rows
    bypass every branch above, which is exactly how a row picks up sentinel zeros, a
    stale offshore string, or a missing ownership note."""
    def num(v):
        try: return float(v)
        except (TypeError, ValueError): return None
    problems = []
    for x in out:
        who = (x.get('verified_company') or x.get('company') or x.get('contact_id'))[:28]
        def flag(msg): problems.append('%-30s %s' % (who, msg))

        # A total of 0 is arithmetically unreachable — it can only be a sentinel.
        for f in ('proven_fit_score','ideal_fit_score','proven_fit_company','ideal_fit_company'):
            if num(x.get(f)) == 0:
                flag('%s is 0 — scores are never zeroed; blank means not assessed' % f)

        # route <-> review_reason must agree
        if x.get('route') == 'Review' and not (x.get('review_reason') or '').strip():
            flag('route=Review with no review_reason')
        if (x.get('review_reason') or '').strip() and x.get('route') != 'Review':
            flag('review_reason set but route=%s' % x.get('route'))

        # ownership must survive on anything a human will look at
        # ownership is required wherever research ran. A row reviewed *because* research
        # could not run has nothing to record, and demanding it would invent evidence.
        NO_RESEARCH = {'not_researched','offshore_small_sample','contact_left_company','no_apollo_match','firmographics_unavailable'}
        if (x.get('route') in ('Work','Review')
                and x.get('review_reason') not in NO_RESEARCH
                and not (x.get('ownership') or '').strip()):
            flag('route=%s with no ownership recorded' % x.get('route'))

        # route and eval_group must be inside their declared enums — an out-of-enum value
        # breaks a CRM import and is invisible in a spot check.
        if x.get('route') not in ('Work', 'Review', 'Disqualified'):
            flag('route=%r is not a valid enum value (Work/Review/Disqualified)' % x.get('route'))
        if (x.get('eval_group') or '') not in ('work', 'holdout'):
            flag('eval_group=%r is not a valid enum value (work/holdout)' % x.get('eval_group'))

        # The rubric makes a verified email a requirement of the Proven-Fit Hot tier (its
        # "Weighting note"). Capping Hot at Qualified would be a tiering change the rubric
        # does not state, so this STOPS the batch and names the rows instead of silently
        # retiering them. Resolve the rows, or ship the violation visibly with the reason
        # written into the run doc.
        if x.get('proven_fit_tier') == 'Hot' and (x.get('verified_email_status') or '') != 'verified':
            flag('proven_fit_tier=Hot but verified_email_status=%r — the rubric requires a '
                 'verified email for Proven-Fit Hot' % x.get('verified_email_status'))

        # a caveat must not contradict the row it sits on
        if 'no domain on record' in (x.get('offshore_check') or '') and (x.get('domain') or '').strip():
            flag('offshore_check says "no domain on record" but domain=%s' % x.get('domain'))

        # tiers must follow their score, and blank when there is none
        for s, t in (('proven_fit_score','proven_fit_tier'), ('ideal_fit_score','ideal_fit_tier'),
                     ('proven_fit_company','proven_fit_company_tier'),
                     ('ideal_fit_company','ideal_fit_company_tier')):
            v, tier_v = num(x.get(s)), (x.get(t) or '').strip()
            if v is None and tier_v not in ('', 'Invalid'):
                flag('%s is blank but %s=%s' % (s, t, tier_v))
            if v is not None and tier_v == 'Invalid':
                flag('%s=%s but %s=Invalid' % (s, v, t))

        # enrich-contact means there is no email to use
        # enrich-contact means the LIVE pass found no usable email. A stale address on the
        # saved Contact does not contradict it — that is the snapshot, not a verified address.
        if x.get('contact_company_mismatch') == 'enrich-contact' and (x.get('verified_email') or '').strip():
            flag('contact_company_mismatch=enrich-contact but verified_email is populated')

    if problems:
        print('\n!! %d INVARIANT VIOLATION(S) — the rubric says these cannot happen:' % len(problems))
        for p in problems[:40]: print('   ' + p)
        if len(problems) > 40: print('   ... and %d more' % (len(problems) - 40))
    else:
        print('invariants: clean')
    return problems

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='run-config.json')
    cfg = json.load(open(ap.parse_args().config))

    CAMPAIGN   = cfg['campaign']
    SCORE_DATE = cfg['score_date']
    RUBRIC     = cfg.get('rubric_version', RUBRIC_SUPPORTED)
    MODE       = cfg['scoring_mode']          # 'fully scored' | 'scored without Linkedin API access'
    P          = cfg.get('paths', {})
    if RUBRIC != RUBRIC_SUPPORTED:
        extra = ''
        if re.fullmatch(r'v?\d+\.\d+\.\d+', (RUBRIC or '').strip()):
            extra = (f'\n\n`rubric_version` carries major.minor only — write {RUBRIC_SUPPORTED}. '
                     f'The third digit is the kit patch level, which by definition cannot change '
                     f'a scored value, so it must never reach a row: two batches that are '
                     f'arithmetically identical would stop matching on the comparability key. '
                     f'Record the kit version ({KIT_VERSION}) in the run doc instead.')
        sys.exit(f'This scorer implements {RUBRIC_SUPPORTED}; config asks for {RUBRIC}. '
                 f'Update the scorer deliberately — do not silently relabel scores.{extra}')

    path = lambda k, d: P.get(k, d)
    J        = json.load(open(path('judgments','judgments.json')))
    for k in J:
        if k not in JUDGEMENT_KEYS: sys.exit(f'Unknown judgments.json key: {k}')
    g        = lambda k: J.get(k, {})
    off      = json.load(open(path('offshore','offshore.json')))
    matched  = json.load(open(path('matched','matched.json')))
    roster   = {r['contact_id']: r for r in csv.DictReader(open(path('roster','roster.csv')))}
    rows     = list(csv.DictReader(open(path('verified','verified.csv'))))

    unknown_es = sorted({(r.get('email_status') or '').strip() for r in rows}
                        - KNOWN_EMAIL_STATUS)
    if unknown_es:
        sys.exit('CANNOT RUN: verified.csv carries email_status values this scorer does not '
                 'map: %r.\nLayer 2 would score every one of them 0. Normalise them in '
                 'verified.csv first — an upload-sourced address (Apollo "User Managed") maps '
                 'to "unverified", an Apollo-validated address to "verified", no address to "".'
                 % unknown_es)

    # Can matched.json answer the departure question at all? Established once, up front,
    # so the answer is a stated fact rather than an accident of a dict lookup missing.
    DEPARTURE_TEST_OK, DEPARTURE_TEST_WHY = _matched_supports_departure_test(matched, roster)

    # domain -> LinkedIn company URL, harvested from research evidence and the Layer 3B
    # recovery passes. Optional: absent file means the column ships empty, which is the
    # honest rendering of "we never captured it".
    try:
        li_urls = json.load(open(path('li_urls','intermediates/li-urls.json')))
    except FileNotFoundError:
        li_urls = {}
        print('NOTE: no li-urls.json — li_company ships empty on every row. Those blanks '
              'are a missing file, not evidence that these companies have no LinkedIn page.')

    res = {}
    for line in open(path('research','research.txt')):
        if not line.strip(): continue
        f = line.rstrip('\n').split('|')
        res[f[0]] = dict(acq=f[1], acq_detail=f[2], distress=f[3], competitor=f[4],
            hiring=int(f[5]), web=int(f[6]), ticket=int(f[7]), growth=int(f[8]), messy=int(f[9]),
            followers=f[10], posts=f[11], range=f[12], median=f[13],
            li_mkt=int(f[14]), li_growth=int(f[15]), li_hire=int(f[16]), note=f[17], urls=f[18])

    out = []
    for r in rows:
        src  = roster.get(r['contact_id'], {})
        cid  = r['contact_id']
        d    = r['domain']
        snap = (src.get('domain') or '').strip()
        left_snapshot = False

        # v3.1 snapshot rule: a blank live organization is usually a DEPARTURE signal.
        # Only trust the snapshot domain when live employment is still open-ended.
        if not d and snap:
            answer, unanswerable = _open_ended_at(matched, src, DEPARTURE_TEST_OK)
            if unanswerable:
                # The question is real and we cannot answer it. Stop rather than guess:
                # guessing False marks a working contact as departed and voids their score.
                sys.exit(
                    f'CANNOT RUN: contact {cid} has no live domain but the saved list has one '
                    f'({snap}), so the run needs the snapshot-vs-live departure test — and it '
                    f'cannot be answered for this contact: {unanswerable}.\n'
                    f'matched.json must hold the RAW people_match responses keyed by '
                    f'person_id, including employment_history (TG-run-playbook.md §2). '
                    f'Re-key or re-run the Apollo pass keeping the raw JSON, or resolve this '
                    f'contact by hand in judgments.json under `left` or `row_overrides`.')
            if answer: d = snap
            else:      left_snapshot = True

        o, R = off.get(d), res.get(d)
        dq, review, caveats = [], [], []

        if left_snapshot:
            review.append('CONTACT LEFT COMPANY — ' + (g('left').get(cid) or
                ('Apollo returns no current organization for this person; last recorded role '
                 + _last_role(matched, src))))
            caveats.append(f"SNAPSHOT vs LIVE: the saved list places this contact at "
                         f"{src.get('company') or '?'}; the live People record does not. "
                         f"Verify the employer before any research or outreach.")
        elif not d:
            review.append('No company domain on record — cannot run the offshore or ownership checks')
        elif not o:
            review.append('Domain not covered by the offshore screen')
        elif o['verdict'] == 'DISQUALIFY':
            dq.append(f"OFFSHORE {o['num']}/{o['den']} indexed employees = {o['pct']}% "
                      f"in {OFFSHORE_COUNTRIES} (>5% threshold)")
        elif o['verdict'] == 'REVIEW':
            review.append(f"OFFSHORE {o['num']}/{o['den']} = {o['pct']}% but only {o['den']} "
                          f"indexed employees — small-sample guard, human call")

        # A domain that cleared the offshore screen but has no research line still scores
        # Layer 3 = 0. The rubric is explicit that such a total is NOT a score — up to 45
        # points were never contestable — so it routes to Review as not_researched rather
        # than reading as a Nurture verdict.
        if d and o and not R and not left_snapshot:
            review.append('Domain not covered by the research pass — Layer 3 never ran, so up '
                          'to 45 points were never contestable')

        # Company is real and researched, but Apollo indexes no employee count: size, revenue
        # band and the offshore ratio are all uncomputable. That is firmographics_unavailable.
        if d and R and not str(r.get('emp') or '').strip():
            review.append('FIRMOGRAPHICS UNAVAILABLE — Apollo indexes no employee count at this '
                          'domain, so size, revenue band and the offshore ratio cannot be computed')

        if d and snap and d == snap and not r['domain']:
            caveats.append(f'DOMAIN RECOVERED from the saved-list snapshot ({snap}) — live '
                         f'People record confirms current employment')
        ok, note = _corroborated(d, r.get('email') or src.get('email'))
        if not ok and d in g('domain_confirmed'):
            caveats.append(f"DOMAIN CONFIRMED despite an email-domain mismatch — {g('domain_confirmed')[d]}")
        elif not ok:
            # append, not insert: if the row already has a stronger trigger that one stays
            # primary and drives review_reason; this note trails it.
            review.append(note); caveats.append(note)

        if d in g('parent_control_confirmed'):
            dq.append(f"BUYING RUNS THROUGH PARENT (operationally confirmed) — {g('parent_control_confirmed')[d]}")
        if d in g('distress'):    dq.append(f"DISTRESS — {g('distress')[d]}")
        if d in g('competitor'):  dq.append(f"COMPETITOR — {g('competitor')[d]}")
        if d in g('pe_recent'):   review.append(f"RECENT PE RECAP — {g('pe_recent')[d]}")
        b2c_note = (f"B2C penalty applied — company-type and industry scored 0: {g('b2c')[d]}"
                    if d in g('b2c') else '')

        mismatch = 'aligned'
        if cid in g('left'):
            mismatch = 'contact-left-company'   # detail is carried in the verdict
        elif cid in g('unverifiable'):
            mismatch = 'contact-unverifiable'
        elif left_snapshot:
            mismatch = 'contact-left-company'
        elif cid in g('mismatch_review'):
            review.append('EMPLOYER MISMATCH — ' + g('mismatch_review')[cid])
        if not r['email'] and mismatch == 'aligned':
            mismatch = 'enrich-contact'   # derivable from email_status; no caveat needed

        # ---- Layer 1
        # B2C is a heavy score penalty, not a disqualifier: company type and industry both
        # score 0. The verdict announces that penalty, so the numbers must actually move.
        if d and d in g('b2c'):
            if d in g('ctype_override') or d in g('ind_override'):
                sys.exit(f'judgments.json: {d} is listed under b2c and also carries a '
                         f'ctype_override/ind_override. They contradict — the B2C rule scores '
                         f'both criteria 0. Remove whichever is wrong.')
            ct, ind = 0, 0
        else:
            ct  = g('ctype_override').get(d, 12 if (R and R['ticket']==5) else 7)
            ind = g('ind_override').get(d, IND_BY_APOLLO.get(r.get('industry'), 8))
        L1P = dict(company_type=ct, size=size_p(r['emp']), title=title_p(r['new_title'], r['seniority']),
                   deal=deal_p(r['rev']), geo=geo_p(r['country']))
        L1I = dict(industry=ind, size_x_title=size_x_title(r['emp'], r['seniority']),
                   revenue=revenue_i(r['rev']), persona=persona_i(r['new_title'], r['seniority']),
                   geo=geo_i(r['country']))
        # ---- Layer 2
        es = r['email_status']
        L2 = dict(email=8 if es=='verified' else 4 if es in ('unverified','extrapolated','likely to engage') else 0,
                  phone=4 if src.get('direct_phone') else 0, linkedin=3 if src.get('li_person') else 0)
        # ---- Layer 3
        if R:
            L3A = dict(hiring=R['hiring'], web=R['web'], ticket=R['ticket'], growth=R['growth'], messy=R['messy'])
            L3B = dict(mkt=R['li_mkt'], growth=R['li_growth'], hire=R['li_hire'])
        else:
            L3A = dict(hiring=0, web=0, ticket=0, growth=0, messy=0); L3B = dict(mkt=0, growth=0, hire=0)
            # derivable from layer3a_web/layer3b_linkedin == 0 and review_reason=not_researched

        l1p, l1i = sum(L1P.values()), sum(L1I.values())
        l2, l3a, l3b = sum(L2.values()), sum(L3A.values()), sum(L3B.values())

        # v3.1: scores are always real. A disqualifier is recorded in `route`, never by zeroing.
        Pv, Iv = l1p+l2+l3a+l3b, l1i+l2+l3a+l3b
        PC = round(100*((l1p-L1P['title'])+l3a+l3b)/PC_DIVISOR)
        IC = round(100*((l1i-L1I['persona']-L1I['size_x_title'])+l3a+l3b)/IC_DIVISOR)

        # v3.1 parent-control test: branding-only evidence goes to a human when the lead is
        # otherwise worth working, and is dropped when it is not.
        if d in g('parent_control_inferred'):
            if max(Pv, Iv) >= 60: review.insert(0, f"INDEPENDENT BUYING AUTHORITY UNCONFIRMED — {g('parent_control_inferred')[d]}")
            else: dq.append(f"PARENT-CONTROLLED BUYING (branding evidence only) and below the Qualified gate — {g('parent_control_inferred')[d]}")

        # UNKNOWN ownership routes to Review when the lead is otherwise Qualified+. Gated on
        # Qualified+ for the same reason the parent-control test is: below the gate, a human's
        # attention is better spent elsewhere.
        if (R and (R['acq'] or '').strip().upper() == 'UNKNOWN' and max(Pv, Iv) >= 60
                and not any(d in g(k) for k in ('serial_acquirer', 'pe_backed', 'pe_recent',
                                                'parent_control_inferred', 'parent_control_confirmed'))):
            review.append(f'OWNERSHIP UNKNOWN — could not determine whether {d} buys '
                          f'independently; establish ownership, then re-route')

        # An unusable contact is a question about the COMPANY: is there a better persona to
        # go after? That only deserves a human when the company itself clears the bar — so the
        # route is gated on the company score, exactly as the parent-control rule is. Without
        # the gate, a departed contact at a 22/22 company sits in a queue with nothing to find.
        invalid = mismatch in ('contact-left-company', 'contact-unverifiable')
        if invalid and not dq:
            already = any(s.startswith(('CONTACT LEFT COMPANY','CONTACT UNVERIFIABLE')) for s in review)
            label = ('CONTACT LEFT COMPANY — the scored contact is no longer at this company'
                     if mismatch == 'contact-left-company' else
                     'CONTACT UNVERIFIABLE — the person could not be placed at this company by any key')
            if max(PC, IC) >= 60:
                # worth a human: there is a real company here to find a better persona at
                if not already: review.insert(0, label)
            else:
                # the gate applies even when a specific message is already queued — otherwise a
                # curated note keeps a 22/22 company in the Review pile with nothing to retarget to
                dq.append('%s, and the company scores %d/%d — below the Qualified gate, so there is '
                          'no persona worth retargeting' % (label, PC, IC))

        # `route` enum is Work/Review/Disqualified (method/3-field-schema.md). A fourth
        # value such as 'Nurture' is out of enum and breaks a CRM import; the Nurture
        # judgement is already carried by the tier columns, so an unflagged low scorer routes
        # Work and is held out of execution by eval_group.
        route = 'Disqualified' if dq else 'Review' if review else 'Work'
        # review_reason belongs to Review rows only. A disqualified row can also carry a
        # review trigger (offshore drop + employer mismatch); the drop wins and the reason
        # must not leak, or a CRM filter on review_reason pulls in dropped companies.
        # Gate 3: the holdout is reserved from the PRE-FLAG population. Assigning it after
        # dq/review empties the holdout, because a low scorer that survives the disqualifiers
        # usually trips a Review flag.
        # NOTE: this makes eval_group a pure function of score — the holdout is every unworked
        # low scorer rather than a random sample, which makes it a weak control. Roadmap item.
        eg    = 'work' if max(Pv,Iv)>=60 else 'holdout'
        verdict = ' | '.join(dq) if dq else (
            (('NEEDS A HUMAN CALL: ' + ' | '.join(review) + '. ') if review else '')
            + (R['note'] if R else 'Not researched.'))
        if b2c_note: verdict += ' ' + b2c_note

        # `PREFIX: detail` — but a blank detail must not ship as a bare "INDEPENDENT:".
        # The trailing colon reads like truncated evidence, when in fact research recorded
        # a verdict and no supporting line. Emit the verdict alone so the absence is honest.
        def _own(prefix, detail):
            detail = (detail or '').strip()
            return f'{prefix}: {detail}' if detail else prefix
        ownership = (_own('SERIAL_ACQUIRER', g('serial_acquirer')[d]) if d in g('serial_acquirer')
                     else _own('PE_BACKED', g('pe_backed')[d]) if d in g('pe_backed')
                     else _own('PE_BACKED', g('pe_recent')[d]) if d in g('pe_recent')
                     else (_own(R['acq'], R['acq_detail']) if R else ''))

        out.append(dict(src, **{
          'verified_company': g('name_fix').get(d, r['new_company']), 'verified_title': r['new_title'],
          'verified_email': r['email'], 'verified_email_status': r['email_status'],
          'employees': r['emp'], 'revenue': r['rev'], 'hq_country': r['hq_country'],
          'proven_fit_score': '' if invalid else Pv, 'ideal_fit_score': '' if invalid else Iv,
          'proven_fit_company': PC, 'ideal_fit_company': IC,
          'proven_fit_tier': 'Invalid' if invalid else tier(Pv),
          'ideal_fit_tier': 'Invalid' if invalid else tier(Iv),
          'proven_fit_company_tier': tier(PC), 'ideal_fit_company_tier': tier(IC),
          'contact_company_mismatch': mismatch, 'crm_status': 'none', 'campaign': CAMPAIGN,
          'eval_group': eg, 'score_date': SCORE_DATE, 'rubric_version': RUBRIC, 'scoring_mode': MODE,
          'route': route, 'review_reason': reason_of(review) if route == 'Review' else '', 'verdict': verdict,
          'record_caveats': ' | '.join(caveats) or '',
          'evidence': (R['urls'] if R else ''),
          'offshore_check': (f"{o['num']}/{o['den']} = {o['pct']}% ({o['verdict']})" if o else 'not run'),
          'ownership': ownership,
          # li_company is the schema's home for the company LinkedIn page. An Apollo export
          # fills it directly; a source list carrying only personal profiles arrives with it
          # empty, in which case research fills it from li-urls.json. Either way the URL goes
          # in this column rather than a near-duplicate beside it. Per-value provenance lives
          # in intermediates/li-urls.json (`source`), not here.
          'li_company': (li_urls.get(d) or {}).get('url', '') or src.get('li_company', ''),
          'li_followers': (R['followers'] if R else ''), 'li_posts': (R['posts'] if R else ''),
          'li_window': (R['range'] if R else ''), 'li_median_engagement': (R['median'] if R else ''),
          'layer1_proven': l1p, 'layer1_ideal': l1i, 'layer2_reach': l2,
          'layer3a_web': l3a, 'layer3b_linkedin': l3b,
        }))

    # A hard disqualifier must be asserted, not hedged. The scorer prefixes an unqualified
    # "COMPETITOR —" / "DISTRESS —", so a hedge in the evidence is erased and a named company
    # carries an allegation nobody actually made. Evidence too thin to state plainly — a
    # hedge, a fetch failure, a bare digit — is too thin to disqualify on.
    HEDGES = ('possible', 'possibly', 'partial', 'partially', 'maybe', 'likely', 'probable',
              'probably', 'potential', 'potentially', 'apparent', 'apparently', 'appears',
              'appear', 'seems', 'seem', 'suspected', 'unclear', 'unconfirmed', 'arguably',
              'perhaps', 'presumably', 'borderline', 'debatable', 'questionable')
    for key in ('competitor', 'distress', 'parent_control_confirmed'):
        for dom, why in g(key).items():
            words = [w.lower().strip(':,;.-()"\'') for w in str(why).strip().split()]
            if not words or not any(words):
                sys.exit(f'judgments.json: {key}[{dom}] has no evidence. A hard disqualifier '
                         f'needs a reason a human can check.')
            # Scan the opening clause, not just the first token: "Staffing firm; possibly a
            # competitor" hedges just as much as "POSSIBLE COMPETITOR" and reads as flat
            # once the scorer prefixes an unqualified "COMPETITOR —".
            hit = next((w for w in words[:8] if w in HEDGES), None)
            if hit:
                sys.exit(f'judgments.json: {key}[{dom}] is hedged — its opening clause says '
                         f'{hit!r}. The scorer states this disqualification unqualified in '
                         f'`verdict`, so the hedge would be erased. Establish it or drop it.')

    cols = set(out[0].keys())
    for cid, ov in g('row_overrides').items():
        bad = [k for k in ov if k not in cols]
        if bad: sys.exit(f'judgments.json row_overrides[{cid}] names columns that do not exist: '
                         f'{bad}. Valid columns are the output schema — check for a renamed field.')
    for x in out:
        x.update(g('row_overrides').get(x['contact_id'], {}))

    validate(out)
    out.sort(key=lambda x: (-(x['proven_fit_score'] or 0), -(x['ideal_fit_score'] or 0)))
    name = f'TG-scored-full-{CAMPAIGN}-{RUBRIC}.csv'
    with open(name, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

    c = collections.Counter
    # The kit version is not a column — it cannot be, since a patch bump must not change a
    # row. It is printed so the run doc can record which build produced the file.
    print(f'kit {KIT_VERSION} · rubric {RUBRIC} · scoring_mode "{MODE}"')
    print(f'wrote {name} — {len(out)} rows')
    print('route:        ', dict(c(x['route'] for x in out)))
    print('review_reason:', dict(c(x['review_reason'] for x in out if x['route']=='Review')))
    print('proven tier:  ', dict(c(x['proven_fit_tier'] for x in out)))
    print('ideal tier:   ', dict(c(x['ideal_fit_tier'] for x in out)))
    hold = sum(1 for x in out if x['eval_group']=='holdout')
    if not hold:
        print('\n!! WARNING: eval_group has NO holdout rows. Every low scorer was routed to '
              'Review or Disqualified, so this campaign has no low-score control and its '
              'forward performance cannot be measured. Reserve the holdout BEFORE applying '
              'Review flags — see method/2-run-playbook.md.')

if __name__ == '__main__':
    main()
