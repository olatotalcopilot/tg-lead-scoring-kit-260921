# TG Sales — Shared Field Schema (Apollo ⇄ CRM)

**Purpose:** one canonical set of custom fields, created identically in **both** Apollo and the
CRM, so scores and campaign membership stay in sync across the two systems. Create these once in
each platform before the first scoring run. Match the **type** exactly — a number field must be
a number in both, an enum must be a dropdown with the same allowed values in both. That is what
makes CSV sync lossless and reporting consistent.

**The per-system mapping table at the bottom is the checklist.** It lists every field to create
and it is the one place to count from. The group counts in the section headings below are
navigation, not a second source of truth; if they ever disagree with the table, the table is
right.

---

## The fields

### Score fields (9)

| Canonical key | Type | Allowed values / range | Notes |
|---|---|---|---|
| `proven_fit_score` | Number | 0–100 | Contact-level. Source of truth. **Never zeroed by a disqualifier** — `route` records that. |
| `ideal_fit_score` | Number | 0–100 | Contact-level. Source of truth. Never zeroed by a disqualifier. |
| `proven_fit_company` | Number | 0–100 | Company-level, shared by all contacts at that company. |
| `ideal_fit_company` | Number | 0–100 | Company-level. |
| `proven_fit_tier` | Enum | Hot / Qualified / Nurture / Skip / Invalid | Derived from `proven_fit_score`, **capped at Qualified when `verified_email_status` is not `verified`** — the rubric makes a verified email a requirement of Proven-Fit Hot. The score itself is never capped, so the two columns together show where a reveal credit would buy a Hot lead. |
| `ideal_fit_tier` | Enum | Hot / Qualified / Nurture / Skip / Invalid | Derived from `ideal_fit_score`. |
| `proven_fit_company_tier` | Enum | Hot / Qualified / Nurture / Skip | Derived from `proven_fit_company`. |
| `ideal_fit_company_tier` | Enum | Hot / Qualified / Nurture / Skip | Derived from `ideal_fit_company`. |
| `contact_company_mismatch` | Enum | aligned / retarget-persona / enrich-contact / contact-left-company / contact-unverifiable / job-change-followup | Routing flag. |

### Routing (2)

| Canonical key | Type | Allowed values | Notes |
|---|---|---|---|
| `route` | Enum | Work / Review / Disqualified | The operational outcome. **This is where a disqualification is recorded** — the scores stay real. `Work` = pursue; `Review` = a human must decide before pursuing; `Disqualified` = do not pursue. Exactly three values; a fourth breaks a CRM import. |
| `review_reason` | Enum | pe_recent_recap / ownership_unknown / offshore_small_sample / employer_mismatch / contact_left_company / contact_unverifiable / no_apollo_match / not_researched / firmographics_unavailable | Blank unless `route = Review`. **Keep `unconfirmed_independent_buying_authority` in the dropdown even though nothing emits it any more** — rows scored before parent control stopped routing still carry it, and removing the value breaks them. Names the trigger so the queue can be triaged and worked in batches of like kind. |

### Justification (3)

These carry the *why* behind a drop or a Review. Long text in both systems, except `li_company`.

| Canonical key | Type | Format | Notes |
|---|---|---|---|
| `ownership` | Long text | `PREFIX: free-text detail`, or the bare prefix when nothing was found | Prefix ∈ INDEPENDENT / PE_BACKED / SERIAL_ACQUIRER / ACQUIRED_RECENT / ACQUIRED_OLD / SUBSIDIARY / UNKNOWN. The prefix determines which rule applies; the detail lets a human re-derive the call without redoing the research. Required on every `Work` and `Review` row. **A parent finding must always reach this column**: since it changes no route, this is the only durable record that the caveat existed, and the scorer raises a violation if a verdict states one that `ownership` does not carry. Not required where research never ran at all: an upstream offshore disqualification, or a Review row whose `review_reason` is itself `not_researched`, `offshore_small_sample`, `contact_left_company`, `no_apollo_match` or `firmographics_unavailable`. Those rows have no ownership evidence to record and demanding a value would invent one. Example: `PE_BACKED: growth investment 2022-09; minority co-investor; management still leads`. |
| `offshore_check` | Long text | `<offshore>/<indexed> = <pct>% (PASS\|REVIEW\|DISQUALIFY)`, or `not run` | The raw ratio behind the offshore rule, kept so a reviewer can judge a small-sample case without re-querying Apollo. Example: `1/75 = 1.3% (PASS)`. Use these three verdicts only; `FAIL` and `GUARD` are not valid values. A `0/0 = 0.0% (PASS)` is an absence of data, not a measured negative — annotate it in `offshore.json`. |
| `li_company` | Short text | Full `https://www.linkedin.com/<company\|school\|showcase>/<slug>` URL, or blank | The company's LinkedIn page, so a rep can open it without searching. Normally a carried-through Apollo export column; when the source list has no company LinkedIn (a spreadsheet carrying only personal profiles, say) it is populated from research instead, with per-value provenance in the run's `li-urls.json`. **A blank never means "this company has no LinkedIn page"** — it means the URL was not captured: the page was measured and the link discarded, the row has no domain, the lookup was skipped because the row was already disqualified, or the API missed. Read `li_followers` to tell them apart — a blank URL beside a non-zero follower count is the recoverable case. Populate from the `linkedin_url` field of the raw company response, never by pattern-matching a citation without checking the slug against the company, or a Hot row acquires a link to the wrong business. Watch for slug shapes that pass a naive check: careers pages, a `_2` duplicate-page suffix, and an unescaped `&`. |

### Carried-through firmographics (1)

| Canonical key | Type | Notes |
|---|---|---|
| `hq_country` | Text | The company's headquarters country, from Apollo — **not computed, not scored**. Geography follows the *contact*, so a US-based buyer at a foreign-HQ company earns full geography points and the company's own location touches the score nowhere. This column is the audit trail for that decision: it keeps a US-buyer / foreign-HQ split visible. **It is not evidence about anything else** — not labour costs, not delivery location, not capability. |

### CRM status (1, advisory — never folded into the score)

| Canonical key | Type | Allowed values | Notes |
|---|---|---|---|
| `crm_status` | Enum | existing_customer / engaged_positive / not_interested / non_target / stale / worked_no_progress / none | CRM history for human consideration. Does NOT change the score, because CRM labels are unreliable. Drives the pursue/suppress/route decision only. |

### Campaign & tracking fields (5)

| Canonical key | Type | Allowed values / range | Notes |
|---|---|---|---|
| `campaign` | Text/Enum | e.g. `2026-09_GA-Founders` | The join key that ties a cohort across Apollo and the CRM. The same value on every lead in the batch. |
| `eval_group` | Enum | work / holdout | `work` = scorers to pursue; `holdout` = retained low-score sample for forward evaluation, which guards against selection bias. |
| `score_date` | Date | ISO date | When the lead was scored — drives decay tracking and re-score cadence. |
| `rubric_version` | Text | e.g. `v3.3` | Which rubric produced the score, so re-scores stay comparable over time. |
| `scoring_mode` | Enum | fully scored / scored without Linkedin API access | Whether Layer 3B was assessed. Together with `rubric_version` this is what makes scores apples-to-apples: only compare leads sharing BOTH. |

### Supporting text (long text)

`verdict` — plain-English **judgement and action**: why the row is routed as it is, the specific
question a reviewer must answer, and the recommended next step (retarget this persona, backfill
that company). On a Review row it must state the question.

`record_caveats` — **provenance only**, and blank in the normal case: what was *changed* about
this record, or what is not *trusted* in it. Valid contents are things like `DOMAIN CORRECTED`,
`RECORD CORRECTED`, `SNAPSHOT vs LIVE`, `DOMAIN RECOVERED`, `DOMAIN NOT CORROBORATED`,
`REVENUE CONFLICT`, `OWNERSHIP CONFLICT`, `STALE FIRMOGRAPHICS`, `EMAIL RECOVERED`, `DNC`, and
single-source or unverified evidence. **Nothing derivable from another column belongs here** —
"no email on file" restates `verified_email_status`, "no Layer-3 research" restates the `layer3*`
columns, "verify current employer" restates `review_reason`. Prose that narrates structured data
makes the column look full while adding nothing. Expect it populated on roughly one row in seven.

`evidence` — links backing Layer-3 and ownership claims; semicolon-separated.

---

## What the CSV contains beyond these fields

A scored CSV has ~60 columns, not 23. The difference is intentional and falls into three tiers.
Only the first needs custom fields creating.

1. **Canonical synced fields (20 structured + 3 long-text)** — everything tabled above. These are
   the ones to create in both systems.
2. **Carried-through source columns** — the list export passed through unchanged (`contact_id`,
   `person_id`, `first`, `last`, `title`, `company`, `domain`, `website`, `li_company`,
   `li_person`, `email`, `email_status`, `direct_phone`, `city`, `state`, `country`, `org_id`,
   `account_id`, `created`, `label_ids`, `founded`) plus the verified overlay the Apollo pass
   produces (`verified_company`, `verified_title`, `verified_email`, `verified_email_status`,
   `employees`, `revenue`). These already exist natively in both systems; do **not** create
   custom fields for them. They are in the CSV so it is self-contained and so it is always
   visible what fed a score.
3. **Run diagnostics** — `layer1_proven`, `layer1_ideal`, `layer2_reach`, `layer3a_web`,
   `layer3b_linkedin`, `li_followers`, `li_posts`, `li_window`, `li_median_engagement`. These let
   anyone re-derive a total or audit a sub-score without re-running research. **CSV and run
   folder only** — they do not belong in the CRM.

So the expected result of diffing scorer output against this schema is: every declared field
present, plus ~36 columns from tiers 2 and 3. That is not drift. Drift is a *declared* field the
scorer does not emit, or a declared field emitted under a different name.

**Note on `domain`.** The `domain` column echoes the roster snapshot. Where the live Apollo pass
resolved a different domain, the scores and the offshore ratio were measured on the **live**
one, and a CRM reader cannot tell that from the row alone. Treat `domain` as provenance, not as
the domain that was scored.

---

## Per-system mapping (fill in once created)

Record each platform's actual field name or API key next to the canonical key, in case a platform
constrains naming.

| Canonical key | Type | Apollo field name | CRM field name |
|---|---|---|---|
| `proven_fit_score` | Number | (create) | (create) |
| `ideal_fit_score` | Number | (create) | (create) |
| `proven_fit_company` | Number | (create) | (create) |
| `ideal_fit_company` | Number | (create) | (create) |
| `proven_fit_tier` | Enum | (create) | (create) |
| `ideal_fit_tier` | Enum | (create) | (create) |
| `proven_fit_company_tier` | Enum | (create) | (create) |
| `ideal_fit_company_tier` | Enum | (create) | (create) |
| `contact_company_mismatch` | Enum | (create) | (create) |
| `route` | Enum | (create) | (create) |
| `review_reason` | Enum | (create) | (create) |
| `ownership` | Long text | (create) | (create) |
| `offshore_check` | Long text | (create) | (create) |
| `hq_country` | Text | (create) | (create) |
| `crm_status` | Enum | (create) | (create) |
| `campaign` | Text/Enum | (create) | (create) |
| `eval_group` | Enum | (create) | (create) |
| `score_date` | Date | (create) | (create) |
| `rubric_version` | Text | (create) | (create) |
| `scoring_mode` | Enum | (create) | (create) |
| `verdict` | Long text | (create) | (create) |
| `record_caveats` | Long text | (create) | (create) |
| `evidence` | Long text | (create) | (create) |

**23 fields total** — 20 structured plus 3 long-text. `li_company` is not in this list because it
is a native export column in both systems, not a custom field. Tick each row as you create it in
both systems.

---

## Sync principles

- **Numerics are the source of truth; tiers and flags are derived.** If you retune thresholds,
  recompute tiers from the stored numeric rather than hand-editing.
- **`route` carries the disqualification, not a zeroed score.** A disqualified lead keeps its
  real numbers so the decision stays auditable and reversible. Filter on `route`, never on
  `score = 0`.
- **Match and join keys are the native fields** (email → LinkedIn URL → company domain), not the
  custom fields. Those are how a contact is matched between systems.
- **`campaign` is the reconciliation key.** To compare the two systems, filter both by the same
  campaign value.
- **One direction of truth per field.** Scores originate in the scoring run (Apollo write-back →
  CRM import); the CRM owns downstream outcome fields (deal stage, reply, meeting) that later
  feed the holdout evaluation.
- **Justification fields travel with the score.** `ownership`, `offshore_check`, `verdict`,
  `record_caveats` and `evidence` are written by the same run that writes the scores. A score
  that reaches the CRM without them is not auditable — nobody can tell later why a company was
  dropped, and the next run pays for the research again.
