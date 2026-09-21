# TG Sales Agency — Dual Lead Scoring Rubric

**`rubric_version` = `v3.1`**
**Scores:** Proven-Fit Score (`proven_fit_score`) · Ideal-Fit Score (`ideal_fit_score`)

This document owns **what to score, the weights, the disqualifiers, the tiers, the routes and
the review reasons.** Nothing else in the kit restates them. If this file and any other file
disagree, **this file wins and the other is the bug.**

**Company:** tgsalesagency.com

---

## The model

Every lead gets TWO scores, 0–100 each, scored independently:

- **Proven-Fit (P)** — *how much does this lead look like the customers we have actually closed?*
  Derived from 50 won deals plus a 205-contact Appointment/Interested cohort.
- **Ideal-Fit (I)** — *how well does this lead match the ICP sheet?* 51–500 employees,
  $10–100M revenue, the primary/secondary/additional industry lists.

**Why two.** Historical wins are founder-led, sub-50-employee service businesses buying
$5–12K engagements. The ICP sheet targets larger, higher-revenue companies. One score would
hide that gap. Two scores make it a routing decision: Proven-Fit-hot leads fit the proven
motion, Ideal-Fit-hot leads fit the growth thesis, and leads hot on BOTH are priority #1.

**Shared across both scores:** Layer 2 Reachability, Layer 3 research signals, and the
disqualifiers. Only Layer 1 (Fit) differs. Layer 4 (CRM history) is an **advisory status key
that does not change either score**.

### What the evidence says about the weights

A leak-free backtest of 41 won deals against 80 Non-Target/Not-Interested losers, scored only
on time-stable fit signals, separates winners from losers ~3–4×.

- **Persona and company size are load-bearing.** "Founder/owner/CEO at a sub-50 service
  business" was ~74% of winners against ~22% of losers; ~55% of losers were the wrong persona
  (VP Sales / Director / HR / rep) or oversized (≈0% of winners).
- **Do not over-weight the industry list.** Both groups were service-heavy, so industry did
  little separating.
- **Fit is a strong filter but a weak ranker** among good-fit founders — ~22% of losers were
  high-fit founders who did not convert. Ranking is the job of the research and CRM layers.
- **Email is the winning channel** — email was the last-contact mode for 28 of the 50 wins.

---

## Proven-Fit Score

### Layer 1P — Fit (40 pts)

| Criterion | Pts | Scoring |
|---|---|---|
| Company type | 12 | Service business w/ relationship sales (agency, consulting, construction/trades services, professional services, B2B software/services) = 12 · other high-ticket B2B = 7 · product-only = 3 · B2C = 0 |
| Size | 8 | 1–50 employees = 8 · 51–100 = 6 · 101–200 = 4 · >200 = 1 · **unknown = 0** (see *Unknown size* below) |
| Title | 12 | CEO / Founder / Owner / Co-Founder = 12 · COO/President = 9 · Head of Rev/GTM = 6 · VP Sales/CRO = 4 · other = 3 |
| Deal plausibility | 5 | Can plausibly fund a $5–12K engagement (revenue ~$1M+ or funded) = 5 · unclear = 2 |
| Geography | 3 | US = 3 · Europe/Middle East = 2 · other = 0 — **scored on the contact's location, not company HQ** |

**How to read "Company type"** (and the Ideal-Fit off-list industry test)

- **Intent:** TG wins with businesses that sell high-ticket, relationship-driven services with a
  real (or forming) sales team — not transactional or product-only companies.
- **The sales-motion test**, used to judge any company whose industry is not on the ICP list:
  does it (a) sell to other businesses, (b) at meaningful or complex deal sizes, (c) through
  relationships and a sales team? If yes, treat it as a service business and score it high even
  though its industry is not listed.
- **Worked examples:**
  - 30-person commercial fire-protection contractor, not a listed industry, with sales reps
    selling maintenance contracts → passes → high
  - DTC e-commerce brand selling gadgets → transactional B2C → 0
  - B2B SaaS with a real sales team selling $20K/yr contracts → service-like motion → high
  - Parts wholesaler taking online orders, no sales team → product-only → low

**How to read "Geography"**

- **Intent:** geography is a proxy for *workability* — time-zone overlap, call scheduling,
  currency, contracting norms. Those attach to the person being sold to, not to the address on
  the corporate filing.
- **Rule:** score the contact's own location. A US-based buyer at a company headquartered abroad
  earns full US points. "Europe" is read geographically, not as EU membership, so the UK and
  Switzerland score 2.
- **Worked example:** a Chicago-based VP of Sales at a company with a Toronto HQ → **US, full
  points.** Record the HQ country separately in `hq_country` so the discrepancy stays visible.

**Unknown size.** A blank employee count scores **0**, not the small-company 8. Absence of
evidence is not evidence of being small, and a row with no firmographics must not outscore a
known 120-person company. A researched company with no employee count also routes to Review as
`firmographics_unavailable`, so the number is never acted on without a human.

### Weighting note

Email reachability matters more for Proven-Fit (email closed 28 of 50 wins): treat a verified
email as a soft requirement, and the Proven-Fit **Hot** tier as requiring one. The scorer raises
a violation on any Proven-Fit Hot row without a verified email so a human decides it — it does
not silently retier the row. See *Gates* in the playbook.

---

## Ideal-Fit Score

### Layer 1I — Fit (40 pts)

| Criterion | Pts | Scoring |
|---|---|---|
| Industry | 10 | Primary (consulting; outsourced services biz/strategy/IT/IoT/SaaS; commercial construction & remodeling) = 10 · Secondary (B2B mfrs, equipment, industrial services, wholesale dist.) = 7 · Additional (automotive, wealth mgmt, VC, PE, software dev) = 5 · off-list passing the sales-motion test = up to 8 · B2C = 0 |
| Size × title pairing | 8 | CEO/Founder at 20–200 = 8 · CRO/VP Sales at 100–500 = 8 · CEO at 201–500 = 6 · VP/CRO at 20–99 = 4 (retarget CEO) · other = 3 · <20 or >1000 = 0–2 |
| Revenue | 7 | $10–100M = 7 · $3–10M w/ Seed–Series B = 5 · unknown but plausible = 3 · outside = 0 |
| Title / persona | 10 | CEO/Founder, CRO, VP Sales = 10 · Head of Rev/GTM = 9 · COO/President = 8 · other sales leadership = 4 |
| Geography | 5 | US / Europe / Middle East = 5 · other = 0 — **scored on the contact's location, not company HQ**. Campaign slices never affect the score. |

**How to read "Size × title pairing"**

- **Intent:** the right buyer depends on company size. At a small company the founder/CEO still
  owns revenue and is the buyer; at a bigger company revenue has been handed to a sales leader,
  so the VP Sales / CRO is the buyer and the CEO is too removed. Score the *match* of person to
  size, not either alone.
- **Mapping messy titles:** "Head of Sales / Managing Director (revenue) / SVP Sales" →
  sales-leader = VP Sales/CRO. "President / Managing Partner / Owner" at a small firm →
  founder-equivalent = CEO.
- **Worked examples:**
  - VP of Sales at a 300-person company → right buyer, right size → **8**
  - The same title at a 15-person company → no real sales org yet, the founder is the true
    buyer → **4**, flag "retarget CEO"
  - "President" at a 60-person firm → founder-equivalent → score like CEO/Founder at 20–200 → **8**
  - "Head of Sales" at a 250-person firm → sales leader at the right size → **8**
  - CEO of a 2,000-person company → too big for TG (>1000) → **0–2**

---

## Shared layers (added to BOTH scores)

### Layer 2 — Reachability (Apollo) — 15 pts

Verified email = 8 · unverified = 4 · unavailable = 0 | Direct/mobile phone = 4 | LinkedIn URL = 3

An address supplied on an uploaded workbook rather than validated by Apollo is **unverified**
(4 points), not verified. Apollo's `email_true_status = "User Managed"` maps to `unverified`.

### Layer 3 — Research signals — 45 pts, split by data source

**3A (Web)** uses free web search and fetch and is always run. **3B (LinkedIn)** requires the
gated RapidAPI Fresh-LinkedIn calls and runs only when a LinkedIn page exists.

**Layer 3A — Web research signals (free, always run) — 30 pts**

| Criterion | Pts | What gets checked |
|---|---|---|
| Hiring sales reps (web) | 10 | Sales-rep openings on the company's own careers page / job boards ≤90 days = 10 · 90–180 days = 6 · non-sales hiring = 3 · none = 0. *Web catches self-hosted postings that LinkedIn's job count misses.* |
| Web presence quality | 5 | Real website live + phone number displayed + credible business footprint |
| High-ticket offer | 5 | Services/pricing plausibly $3K+ MRR or a complex/contract sale = 5 · unclear = 2 · low-ticket = 0 |
| Growth/scale language (web) | 5 | Expansion, new markets/offices, recent funding, "ready to grow" — stated on the site, in news or in press. **Sponsor-driven growth counts:** a growth-equity round, a post-recap expansion plan, or a newly hired sponsor-backed revenue leader are all qualifying evidence here. |
| "Messy middle" evidence | 5 | Founder-led sales past ~30 employees; improvised revenue efforts; hiring "hunters" without sales infrastructure |

**A `hiring` score of 0 usually means "not found", not "verified absent".** The two are worth
very different amounts to a reader and no column distinguishes them, so the research note must
say which it is — a careers page that states there are no open positions is a genuine verified
negative and should say so in those words.

**Layer 3B — LinkedIn signals via RapidAPI (gated; costs credits) — 15 pts**

| Criterion | Pts | What gets checked |
|---|---|---|
| Marketing activity vs. traction | 10 | Post cadence + engagement: consistent posting with LOW engagement ("busy but not productive" — the ideal wedge) = 10 · active with real traction = 6 · dormant page = 3 · no page / none = 0 |
| Growth momentum (LinkedIn) | 3 | Follower count and growth, expansion/funding posts corroborating the Layer 3A growth signal |
| Hiring confirmation (LinkedIn) | 2 | LinkedIn hiring posts corroborating or extending the web hiring signal |

**How to read "Marketing activity vs. traction" (the counterintuitive one)**

- **Intent:** TG's best wedge is a company that is *trying* at marketing and getting little back
  — posting regularly yet nobody engages. It signals a company that knows it needs to grow but
  has no working revenue engine, which is exactly TG's pitch. So **low engagement despite
  consistent effort scores HIGHER, not lower.**
- **How to judge:** post cadence (monthly or more?) and engagement (likes/comments per post
  relative to follower count).
- **Worked examples:**
  - Posts 2–4×/month, 0–6 likes each on 1,000 followers → trying hard, no traction → **10**
  - Posts often with strong engagement (dozens to hundreds of likes) → a working marketing
    machine, less of a fit → **6**
  - Has not posted in 6+ months → dormant → **3**
  - No LinkedIn page at all → **0**
- **Where the bands overlap, say which reading you took and why, in the note.** A large firm can
  post consistently, show engagement under ~0.3% of followers *and* draw dozens of reactions per
  post — satisfying both the 10 band and the 6 band at once. Whichever way the row is scored, the
  reasoning must be recorded, so that the same evidence shape is not scored 10 on one row and 6
  on another within a batch.
- **A very small or very new company can score 10 for the wrong reason.** A one-person practice
  posting into an audience of 50 is not a company with a sales function to fix. The score is
  right; the inference it usually supports is not — say so in the note.

**Consistency rule — so scores stay comparable.** Assess Layer 3B the same way for every lead in
a batch:

- *RapidAPI on (recommended):* the free company-by-domain lookup is the universal gate. If a
  LinkedIn page exists → run the engagement calls and score 3B on real data. If no page exists →
  3B scores low **legitimately**; the absence of a LinkedIn presence is itself a signal of thin
  marketing, not missing data. Either way every lead gets a full 0–100 score and all are
  directly comparable.
- *RapidAPI off, for a whole batch:* score the entire batch on Layer 3A plus Layers 1–2 only.
  That is internally consistent, but do not rank it against RapidAPI-scored batches. **Mind the
  tier compression:** the maximum becomes 85, not 100, while the tier cutoffs stay at 80/60/40 —
  so Hot needs 80 of 85 (~94%) and the batch reads systematically colder rather than merely
  incomparable. Do **not** silently rescale to 100; that fabricates precision Layer 3B never
  measured. Either report the tiers as understated and say so in the run doc, or agree a rescale
  explicitly and record it in `scoring_mode`. This is a batch-level mode recorded in
  `scoring_mode`, never a per-row distinction.

**Two comparability axes.** Scores are apples-to-apples only when they share BOTH the same
`rubric_version` AND the same `scoring_mode`. `rubric_version` guards against changes to the
rubric over time; `scoring_mode` guards against comparing a LinkedIn-assessed score with a
web-only one. Always filter on both before ranking or comparing.

**Unresearched rows are not low-scoring rows.** If Layer 3 never ran for a lead — no domain on
record, research budget exhausted, an upstream disqualification short-circuited the pipeline —
the resulting total is **not a score**, because up to 45 points were never contestable. Such
rows set `review_reason = not_researched` and route to Review. Never rank, tier or compare an
unresearched row against a researched one; the deflated number looks like a Nurture verdict and
is not one.

### Layer 4 — CRM status key (advisory; does NOT change either score)

CRM labels are inconsistent and sometimes wrong — a paying customer has been found mislabelled
"Non Target". So CRM history must not inflate or deflate the score; the score stands on fit,
reachability and research alone. Record CRM history as a status the human reads next to the
scores, informing the pursue / suppress / route decision, which is a human call. Stored in
`crm_status`.

| `crm_status` | Meaning | Recommended action (human decides) |
|---|---|---|
| `existing_customer` | Won deal or customer tag | Don't cold-prospect a current customer; feed the win-profile lookalikes |
| `engaged_positive` | Appointment / Interested / Send Info / Future Lead | Prioritise for human follow-up (warm relationship) |
| `not_interested` | Previously declined | Suppress unless there's a strong reason to re-approach |
| `non_target` | Previously marked not-a-fit | Human review — the label is often unreliable; don't auto-drop a high scorer |
| `stale` | Last touched >18 months ago | Treat as effectively net-new |
| `worked_no_progress` | 3+ touches, no advance | Consider deprioritising |
| `none` | No CRM history (fresh Apollo contact) | — |

---

## Ownership classification

Ownership is recorded in `ownership` as `PREFIX: free-text detail`. The prefix determines which
rule applies; the free text and the `evidence` link let a human re-derive the call without
redoing the research. **Ownership never adds or subtracts points** — it decides routing only.

| `ownership` prefix | Meaning | Effect |
|---|---|---|
| `INDEPENDENT` | No parent, no sponsor | Score and route normally |
| `PE_BACKED` | Financial sponsor — growth equity, buyout, recapitalisation | Score and route normally. A recap in the **last ~18 months** routes to Review (spend can be frozen or redirected while new owners set direction). |
| `SERIAL_ACQUIRER` | Decentralised permanent-holding acquirer that runs units autonomously (Constellation Software / Volaris, Valsoft and similar) | Score and route normally — these behave like financial owners, not strategic parents |
| `ACQUIRED_RECENT` | Acquired by a **strategic** parent, ≤24 months | Apply the parent-control test |
| `ACQUIRED_OLD` | Acquired by a **strategic** parent, >24 months | Apply the parent-control test |
| `SUBSIDIARY` | Operates as a unit of a **strategic** parent, date unknown or immaterial | Apply the parent-control test |
| `UNKNOWN` | Could not be determined | Route to Review if otherwise Qualified+ |

A prefix with no supporting detail ships as the bare verdict (`INDEPENDENT`), never as
`INDEPENDENT:` with a trailing colon — the colon reads like truncated evidence when in fact
research recorded a verdict and found no supporting line. Where nothing was found, the research
note should say what was looked at.

**Why ownership is not scored.** Every mechanism by which sponsor backing makes a company a
better prospect is already instrumented in Layer 3A — sales hiring (10 pts), growth/scale
language including funding (5 pts), and messy-middle evidence (5 pts). A company running the
post-investment growth playbook lights up those criteria on observable evidence. A separate
ownership bonus would pay twice for the same fact, and would also fire for cost-cutting recaps
that show none of those signals — precisely the cases where the thesis does not hold. Ownership
therefore routes; Layer 3 scores.

### The parent-control test

**Deal age is not the test. Operational control is.** Ask: *is there observable evidence that
the parent runs this company's hiring, procurement, or web presence?*

- **Operationally confirmed → disqualify, at any deal age.** The careers page or ATS redirects
  to the parent · job requisitions are posted by parent legal entities · the company domain
  redirects to the parent · the brand is retired or fully folded into the parent's. These are
  facts about process, not structure.
- **Inferred from branding only → Review**, if the lead is otherwise Qualified+ on either score.
  "X, an Acme company" in a LinkedIn name or an About page is a marketing statement, not a
  procurement fact. The company may well still buy independently.
- **Otherwise below Qualified → disqualify.** A human's attention is the scarce resource; don't
  spend it on a lead that would not be worked even if the ownership concern evaporated.

**Why branding-only evidence is not a hard disqualifier.** The bar for a hard disqualifier is
that a company be *un-sellable* — no web presence, a competitor, out of business. Each is
directly observed. Parent control inferred from branding is an *inference* about where a
decision sits, and the company still exists with a budget it could spend. The cost asymmetry
reinforces this: a false drop loses a Qualified prospect invisibly and permanently, while a
false include costs one sequence and a reply saying "that goes through our parent now."

### Financial sponsors are not strategic parents

A financial sponsor leaves the company buying independently — its own sales org, its own budget,
its own vendor decisions. Score it normally. This is the distinction between a division of an
operating company (strategic) and a private-equity portfolio company (financial).

**Serial decentralised acquirers are a third case.** Constellation Software / Volaris, Valsoft
and similar perpetual-holding acquirers buy to hold and run units autonomously, each with its
own P&L, leadership and vendor decisions. Structurally they look like acquisitions;
operationally they behave like financial ownership. Tag `SERIAL_ACQUIRER` and score normally. Do
not let a company fall into `ACQUIRED_*` merely because a holding company appears on the About
page — check whether the unit still has its own leadership and careers page.

---

## Disqualifiers

**Hard disqualifiers — do not pursue.** These remove a lead from prospecting entirely, so the
bar is deliberately narrow: only things that make a company *un-sellable* — it cannot or will
not transact — never things that merely make it a weaker fit, because weak fit is what the
scores are for.

*"Will not" includes having a structurally cheaper substitute.* Two rules below rest on that: a
competitor sells what TG sells, and an offshore-heavy company can staff outreach itself for less
than it would pay TG. Neither will buy, so both clear the bar.

A lead is disqualified if any is true:

- It has no discoverable web presence.
- **It is a competitor.** This covers a sales agency or sales-outsourcing firm, *and* any firm
  whose core business is placing people: staffing, recruiting, executive search, RPO, MSP
  staffing, staff augmentation. **Where the boundary sits:** marketing, PR and advertising
  agencies are **not** competitors — they sell creative and media rather than placing people or
  carrying someone else's quota. A firm that mixes staffing with genuine solutions delivery is
  a competitor; a firm that sells a recruiting service as one line inside a different core
  business (an insurance broker with an HR-consulting arm, say) is not. Decide the boundary
  cases explicitly in `judgments.json` and say which way and why — do not leave them flagged.
- It shows clear distress (layoffs, closure, winding down).
- Its buying is **operationally controlled** by a strategic parent — see *The parent-control
  test*. Branding-only evidence routes to Review instead.
- **Offshore workforce concentration >5%** — more than 5% of the company's indexed employees are
  located in typical offshore-delivery countries (India, Philippines, Pakistan, Bangladesh, Sri
  Lanka, Vietnam, Indonesia, and similar).

**A hard disqualifier must be asserted, not hedged.** The scorer states a disqualification
unqualified in `verdict` ("COMPETITOR — ..."), so a hedge in the evidence is erased and a named
company carries an allegation nobody actually made. Evidence too thin to state plainly is too
thin to disqualify on: establish it, or drop the disqualifier and let the score carry the
judgement. The scorer refuses to run on an empty `competitor`, `distress` or
`parent_control_confirmed` judgement, or on one whose opening clause hedges — that is a tripwire
for the obvious cases, not a proof, so read the entries as well.

**Why TG has the offshore rule.** An offshore-heavy company already runs an offshore labour pool
and the management model to direct it, so it can staff the warm and cold outreach TG sells **more
cheaply in-house than it can buy it**. It is not a poor fit — it is a non-buyer with a
structurally cheaper alternative. That is the same logic as the competitor rule, and it is why
the drop is hard rather than a Review. (This rationale is recorded because, left unwritten, the
rule reads as arbitrary policy and gets misclassified.)

*The rule is over-inclusive at its own margin, deliberately.* The mechanism is **capability**,
not headcount share: a firm with six offshore engineers on a product team cannot cheaply spin up
an SDR function, while a firm with 200 offshore delivery staff can. Observed distributions have
been bimodal, with everything in the 5–25% band scoring below 60 on both scales, so the loose
threshold has cost nothing. **Leave the threshold at 5% until a batch shows a Qualified+ company
dying in that band** — that is the trigger to revisit it.

*There is a second route to that substitute, and it is recorded rather than routed.* A company
can run its outreach function in a low-cost labour market without an offshore delivery arm. The
probe is two free Apollo people-search calls (see the playbook) and the result goes in `verdict`
as a positioning note. It does **not** disqualify: too few cases have been seen to make it a
rule. If a second clear case appears, raise it.

### Size is scored, not gated

There is **no minimum-employee disqualifier.** Company size is captured entirely inside the
Layer 1 *Size* sub-score and nowhere else. A 1–4-person founder-led shop remains fully eligible
for both scores; it simply earns few Size points. A sanity check against TG's 50 real won
customers found that hard size floors would have wrongly excluded **40% of actual wins under a
<5-employee Proven-Fit floor and 65% under a <10-employee Ideal-Fit floor** — the win base is
dominated by 1–9-employee businesses. A hard size floor throws out the exact profile TG converts
best. Small size should *lower* a score, never *remove* the lead.

### B2C is a heavy score penalty, not a disqualifier

A purely transactional consumer business is a poor fit and scores **0 on both the Company-type
and the Industry sub-components** of Layer 1, which already drives its total far down. But
"sells to consumers" does not zero both scores outright: real wins exist in consumer-adjacent
categories (coaching/training, e-learning, apparel, wellness). Reserve a true skip for *pure
transactional DTC/retail with no relationship-sales motion*; when a consumer-facing business
still sells a high-ticket, relationship-driven service (a coaching practice, a boutique
advisory), let the low sub-scores speak and keep it in the funnel.

### List-building: the seniority floor

Manager-level titles stay out of the ICP and are excluded at the **list-building filter**, before
a batch is pulled — not by the scorer. The binding constraint is seniority, not reachability: a
Sales/BD Manager with a good email on file is still out. This is consistent with the backtest,
where ~55% of losers were the wrong persona.

The persona bands still score "other sales leadership = 4" rather than 0, because manager-level
rows can arrive from an uploaded workbook rather than an Apollo pull. When they do, they score —
they are not silently dropped.

---

## Routing

`route` is the operational outcome for each row: **Work**, **Review**, or **Disqualified**. It is
derived from the scores plus the disqualifier and ownership rules, and it — not a zeroed score —
is what records a disqualification.

| | Score ≥80 | 60–79 | 40–59 | <40 |
|---|---|---|---|---|
| Per score | Hot | Qualified | Nurture | Skip |

**A disqualified lead keeps its real scores.** Never zero a score to record a disqualification:
`route` carries that. A zeroed score destroys the reviewer's most important input and actively
misleads, because a genuinely strong prospect then displays as 0/0. A total of 0 is
arithmetically unreachable, so a 0 can only ever be a sentinel — the scorer treats one as a
violation.

**`Invalid`** is a fifth *contact*-tier value, outside the numeric scale. It means the
contact-company pairing cannot be scored — the person has left, or the verification pass returned
no match — so no contact score exists to tier. Company tiers are never `Invalid`. Where a company
was never assessed at all, because the contact identity could not be established, the company
scores and tiers are **blank**, never `0` and never `Skip`. A zero is a score someone computed; a
blank is an assessment nobody made, and the difference matters to whoever picks the row up.

**Routing matrix:**

- Hot on Proven-Fit AND Ideal-Fit → Priority 1: sequence + call task now
- Hot on Proven-Fit only → proven-motion pipeline (founder-led, email-first outreach)
- Hot on Ideal-Fit only → strategic pipeline (bigger companies, longer cycle, VP Sales/CRO personas)
- Qualified on either → standard sequence
- Below on both → nurture/skip, carried by the tier columns and `eval_group`, not by `route`

`route` has exactly three values. An unflagged low scorer routes `Work` and is held out of
execution by `eval_group = holdout`; the Nurture judgement is already carried by the tier
columns. A fourth route value breaks a CRM import.

### Review completeness standard

A `Review` row exists to be decided by a human in one sitting. It is **not complete** unless it
carries everything that decision needs:

1. **`verdict` states the question and the recommended action**, in the form
   `NEEDS A HUMAN CALL: <reason> — <the specific thing to determine>`.
2. **`review_reason`** is set to the enum value naming the trigger, so the queue can be triaged
   and worked in batches of like kind.
3. **Scores carry their real values** — never zeroed, never a partial total presented as a score.
   One exception, and only one: when the contact has left, the **contact** scores are blank and
   both contact tiers read `Invalid`, because a contact score is a score of *this person at this
   company* and that pairing no longer exists. The **company** scores stay real and are what the
   reviewer acts on — a departed contact's row carrying company 84/93 is the whole basis of the
   job-change follow-through.
4. **The inputs for that specific question are present.** This is conditional on the reason, not
   a blanket requirement: an ownership question needs `ownership` plus at least one `evidence`
   link; an offshore small-sample question needs the `offshore_check` ratio; a no-Apollo-match
   row needs nothing further.

A reviewer should never have to leave the sheet to answer the question the row poses. If they
would, the row is not ready for Review — finish the research or disqualify it.

**Every question must be answerable from the desk.** This is cold outbound: there is no
relationship, no account team, nobody at the prospect to ask. A flag that says *confirm with the
company* or *check whether they already do X* cannot be executed and is therefore noise — worse
than nothing, because it looks like diligence. Phrase every Review question against evidence a
person can actually reach: the company's site and careers page, its ATS, job postings, LinkedIn,
press, Apollo. If a question can only be answered by talking to the prospect, it is not a Review
question — it is either a research task that must be finished first, or a thing to learn on the
call.

| `review_reason` | Trigger | What the reviewer decides |
|---|---|---|
| `unconfirmed_independent_buying_authority` | Strategic parent, branding evidence only | Does this company still buy independently? |
| `pe_recent_recap` | Financial sponsor, recap ≤18 months | Does the desk evidence show the company still spending — sales roles open, expansion news, leadership stable — or a post-recap freeze? |
| `ownership_unknown` | Ownership could not be determined | Establish ownership, then re-route |
| `offshore_small_sample` | Offshore % over threshold on <~15 indexed employees | Is the ratio real or a sampling artefact? |
| `employer_mismatch` | List, Apollo and web disagree on employer — including a record domain that does not match the contact's email domain | Confirm the current employer, and that the domain is the right company, before outreach |
| `contact_left_company` | Apollo employment history shows a move | Backfill the old company; score the new one |
| `contact_unverifiable` | The contact cannot be placed at this company by any key, but the company clears the Qualified gate | Identify the correct persona at that company |
| `no_apollo_match` | Verification pass returned nothing | Verify the contact manually or drop |
| `firmographics_unavailable` | Company confirmed real, but Apollo indexes no employees at the domain — size, revenue and the offshore ratio cannot be computed | Establish size and a contact route, or drop |
| `not_researched` | Layer 3 never ran — no domain, budget exhausted, or an upstream short-circuit | Worth researching, or drop? |

## Outputs beyond the scores

- Size × title mismatch → recommend the correct persona at the same company
- Evidence links per Layer 3 criterion, for personalisation
- Flag CRM contradictions (status vs. outcome) for human review
- Repair step: infer missing CRM company names from email domains, enrich via Apollo

---

## Field spec

Numeric (0–100): `proven_fit_score`, `ideal_fit_score` (contact-level) · `proven_fit_company`,
`ideal_fit_company` (company-level: all criteria except title/persona and reachability, rescaled
to 0–100; computed ONCE per company and shared by all its contacts). **No CRM modifier** —
Layer 4 is advisory and moves no score, contact-level or company-level.

Derived enums, stored in the CRM because custom fields cannot compute: `proven_fit_tier`,
`ideal_fit_tier`, `proven_fit_company_tier`, `ideal_fit_company_tier` (Hot/Qualified/Nurture/Skip;
contact tiers may also be Invalid).

Routing: `route` (Work / Review / Disqualified) · `review_reason` (enum above; blank unless
route = Review) · `contact_company_mismatch` — aligned · retarget-persona (company qualifies,
contact is the wrong buyer → name the right persona) · enrich-contact (right buyer, missing or
generic email → Apollo enrichment first) · contact-left-company · contact-unverifiable (the
person cannot be placed at this company by any key — identifier, LinkedIn URL, email or
name-at-domain; they were never there, as distinct from having moved on) · job-change-followup.

Justification columns (long text): `verdict` (plain English — judgement **and action**: why the
row is routed as it is, the question on Review rows, and the recommended next step) ·
`record_caveats` (provenance **only** — what we changed about the record or do not trust in it;
never anything derivable from another column; blank is normal) · `evidence` (links backing
Layer-3 and ownership claims) · `ownership` (prefix + detail) · `offshore_check` (the raw ratio,
e.g. `1/75 = 1.3% (PASS)`).

Rationale: numerics are the source of truth (sortable, re-tunable thresholds); enums are derived
conveniences. A high company score with a low contact score IS the retargeting signal. The
justification columns are what make a drop auditable and a Review row workable — without them
the reasoning dies with the run.

---

## Mandatory Apollo verification pass

The Apollo people-match step is REQUIRED before scores are final — never ship proxy-scored
leads. On a 10-lead calibration it invalidated 20% of the sample and re-ranked another 20%:

- Caught contacts who had LEFT their companies, which CRM and web research both missed and
  Apollo employment history caught.
- Found verified work emails for blocked leads at zero credit cost (a standard match returns
  email and status), flipping them from Qualified/Nurture-risk to Hot.
- Corrected wrong LinkedIn URLs and titles on CRM records.
- Around 30% of contacts have NO Apollo match — those keep proxy reachability scores and get
  flagged for manual verification.

**Order of operations per lead:** CRM fields → Apollo people match (free) → web/LinkedIn research
→ score → only then consider credit-spending enrichment for high scorers still missing emails.

### The saved list is a snapshot, not live data

A saved Apollo list contains **Contact** records — copies of a person's fields made in your
workspace at the moment you saved them — while `apollo_people_match` queries Apollo's live
**People** database. They drift apart, so a list export is evidence of what was true on the save
date, not now. Expect on the order of one row in eight to disagree with the live record after a
few weeks; those are what the verification pass exists to find.

**When the live record returns no organization, that is usually a departure signal, not a
missing field.** Do not silently fall back to the list's domain — that scores the contact against
a company they may have left, which is the exact failure the verification pass prevents.

- **Live history has an open-ended role at the company named in the list** → the *contact* is
  confirmed, and only then is the snapshot worth reading. Match on the **company name**, not
  Apollo's `current` flag, which is unreliable (records exist carrying `end_date: null` with
  `current: false`).
- **No such entry** → set `review_reason = contact_left_company`, blank the **contact** scores
  and set both contact tiers to `Invalid`, **keep the company scores real**, and record the last
  known role. The company is still a company, and the company scores are what the job-change
  follow-through acts on. Never use `not_researched` here — that sends a reviewer to research a
  company when the real question is where the person works.

**Confirming the contact does not confirm the domain — corroborate it separately.** Employment
history validates *the person*; the domain on the Contact record is a separate field and can
point at an entirely different company. Recovered snapshot domains have turned out to belong to
entirely different companies more often than not, in different countries and industries, and
would have been screened and scored as the wrong business.

Cheapest corroboration, in order: **the contact's own email domain** (an immediate mismatch is a
red flag), then the live organization name, then a one-page fetch of the site to confirm the
business matches. **Never run the offshore screen or Layer 3 on an uncorroborated domain** — a
passing or failing ratio for the wrong company is worse than no ratio, because it looks like
evidence.

Three distinct failure modes hide behind "the domain was blank", and only the first is
staleness: (1) the snapshot drifted — true on the save date, false now; (2) the live organization
record genuinely lacks a `primary_domain`, with nothing stale about it; (3) Apollo's global
record was already wrong when the list was saved. Apollo is a source here, not an authority.

**An email fallback must be name-corroborated.** When a people-match by identifier returns
nothing, matching by email is the obvious next move — and it is dangerous. Apollo returns
whichever person its database associates with that address, which is not necessarily the person
on your record; a match has resolved to a different named individual in another country and
industry, which would have overwritten a US CEO's title, employer and firmographics wholesale.
**Accept an email-keyed match only if the returned name corroborates the record. A name mismatch
is a false positive, not a match** — treat it as no match and route to Review. The same caution
applies to any fallback key that is not unique to the person.

*Related: a workspace-minted `person_id`.* Apollo People ids are long-lived and historic; a
`person_id` generated in the same period as your Contact ids belongs to a record created in your
workspace, with no entry in the live People database. Such a row can never match by identifier
and, per the rule above, usually should not be matched by email either. It is not a pipeline
failure — it is a record with no external existence to verify. Route to Review.

**Score on the domain, not the Apollo org name.** Apollo org names are unreliable in isolation —
domains routinely return the name of an unrelated company. A name-comparison heuristic once
flagged 21 job changes of which only 5 were real. Confirm a company by research before trusting
a name change, and detect job changes from employment history, never from name comparison.

## Job-change follow-through rule

Every `contact-left-company` record spawns two follow-ups:

1. **Backfill the old company.** It already has company scores — identify the correct persona
   there and propose that contact.
2. **Score the person's NEW company** through both rubrics. Propose adding them ONLY if it clears
   the gate (Qualified+ on either score). If proposed, set
   `contact_company_mismatch = job-change-followup` and note the prior relationship in `verdict`
   — they have history with the team, so the lead is warm. **This is a flag, not a score
   adjustment**; CRM history never moves a number.

A new company that falls short of the gate is tagged "recheck in 6–12 months" rather than
deleted. Expect job changes on a few percent of stale (2+ year) records — a quiet source of
net-new warm leads at batch scale.
