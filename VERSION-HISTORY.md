# Version history

## The versioning convention

**The kit and the rubric share one version line, `major.minor.patch`.** They are not separate
artifacts — the kit *is* the method, packaged — so they carry the same number.

| Digit | Bumped when | Reaches the data? |
|---|---|---|
| **major** | The model changes shape — a new layer, a new score. Everything needs rescoring and old scores are not comparable. | yes |
| **minor** | Anything that *can* change a number, a tier, a route or a column on some row — including a change to routing or recording that leaves the arithmetic alone. | yes |
| **patch** | Nothing about any scored output can change: documents, wording, packaging, or a guard that only refuses malformed input. | **no** |

**Only `major.minor` is written into a row.** `rubric_version` is a comparability key, and the
standing rule is to filter on `rubric_version` *and* `scoring_mode` before ranking anything — so
equality on it has to mean *these rows are comparable*. A patch release cannot change a score by
definition, so letting its digit through would split one comparable population in two. The scorer
refuses a `rubric_version` carrying three digits and names the reason. The kit version is printed
when a batch is scored, and the run doc records it.

The test for the patch digit is **"no scored output can change"**, not "documents only" — that is
what a reader can actually check, and it is where a guard that merely refuses broken input
belongs.

**Scope.** This file records how the *method* and the *kit* changed. It is not a log of scoring
runs — the kit deliberately carries no run history, and each run writes its own run doc.

---

## Releases

### 3.2.1 — 2026-09-22 — *Quick-start instructions*

Documents only. **No rule, no arithmetic and no scored value can differ because of this release.**

- The README now **opens with five numbered steps for the person running a batch**: download and
  unzip the kit, open a session with a connected folder, move the folder into it, check the tools
  are connected, and paste the kick-off prompt (given verbatim, ready to copy). Everything that
  used to come first — what the kit is, how it scores — now follows the instructions.
- The kick-off prompt names the failure mode it exists to prevent: the agent is told not to
  design a method, write a rubric or write a scorer, because all three already exist in the
  folder.

### 3.2.0 — 2026-09-22 — *Parent control is recorded, not a drop*

**Parent control no longer disqualifies a lead, and no longer routes one to Review.** A company
owned by a strategic parent is scored, routed on its merits, and worked — with the finding stated
at the front of `verdict` and preserved in `ownership`.

Why: the old rule dropped a company whose careers page redirected to its parent even when it kept
its own brand, sales team, P&L and budget. One such company was discarded by the rule and then
closed at several times TG's median deal. The rubric's own cost asymmetry settles it — a false
drop loses a Qualified prospect permanently and invisibly, while a false include costs one
sequence and a reply saying "that goes through our parent now."

- **Both grades of evidence are kept, because the rep needs them**, but neither changes a route.
  Operational evidence (careers page or ATS redirecting to the parent, requisitions posted by a
  parent legal entity) produces `PARENT-CONTROLLED BUYING (operational evidence)` plus the
  instruction to establish who signs early. Branding evidence ("X, an Acme company") produces
  `PARENT LINK ON RECORD (branding evidence only)` and the note that the company most likely
  still buys independently.
- **`review_reason = unconfirmed_independent_buying_authority` is retired.** Its question — *does
  this company still buy independently?* — no longer changes the route whichever way it is
  answered, so it cannot earn a human's attention up front. It stays in the schema enum so
  historical rows remain readable; nothing emits it.
- **One ownership case still disqualifies, and it is a different one.** A brand that no longer
  exists as a distinct business — domain redirects to the parent, no separate site — fails the
  existing **no discoverable web presence** test. Research records it as that.
- **A new invariant.** Since the finding changes no route, `ownership` is its only durable
  record. The scorer raises a violation on any row whose `verdict` states a parent finding that
  `ownership` does not carry.
- The self-test fixture gained two parent-controlled companies, one per evidence grade, both
  routing Work.

**Comparability: v3.1 and v3.2 scores are directly comparable.** Layers 1–3 are arithmetically
identical; only what happens to a scored lead changed. **Their `route` values are not
comparable** — a company with a strategic parent was Disqualified under v3.1 and is Worked under
v3.2 — so any count of drops, or any filter on `route`, must be taken one version at a time.

*Follow-up, not included here:* batches scored before 3.2.0 still carry parent-control drops.
They were disqualified under a rule that no longer exists and are worth re-examining; it is a
query against CSVs already held, not a re-run. Tracked as roadmap item 1.

### 3.1.1 — 2026-09-22 — *Repo conventions and synced versioning*

Packaging, documents and one guard. **No rule and no arithmetic changed, and no scored value can
differ because of this release** — which is what makes it a patch.

- **Adopted the single version line described above.** The kit briefly carried its own
  independent `1.0.x` numbering; that is retired, and the mapping is `1.0.0` → `3.1.0`,
  `1.0.1` → `3.1.1`. The `1.0.1` content was never released on its own — it ships here.
- **The scorer enforces the convention.** It already exited on a `rubric_version` it does not
  implement; it now also detects a three-digit value and explains that the patch digit must not
  reach a row. It prints `kit <version> · rubric <version> · scoring_mode <mode>` when it writes
  the CSV, so a run doc can record which build produced the file.
- The run-doc template gained a **Kit** field in its header.
- The self-test gained two cases: a patch digit in `rubric_version`, and a rubric version the
  scorer does not implement. Seven checks now, six of them refusal guards.
- `README-FOR-HUMANS.md` renamed to `README.md`, following the convention for a top-level repo
  file; references updated in the README and `AGENT-START-HERE.md`.
- Version metadata added to the README header, and this file added.

### 3.1.0 — 2026-09-21 — *Packaged kit*

First self-contained release. The method previously lived as loose documents that assumed the
reader already had context; this release makes it runnable from cold by someone who has never
seen it.

- **Assembled the kit**: `AGENT-START-HERE.md` as the single entry point, the four `method/`
  documents, the scorer with its file-format contract and worked examples, the run-doc template,
  and a self-test.
- **Rewrote every document as current-state.** Version change-logs, run narratives and companies
  named from past batches were removed; every rule is stated as a rule that applies now.
- **Wrote settled rulings into the method** rather than leaving them as knowledge carried between
  people: staffing, recruiting, executive search, RPO and staff augmentation are competitors,
  with the marketing/PR boundary stated; manager-level titles are excluded at the list-building
  filter; a LinkedIn lookup is retried by URL before "no page" is recorded; identifiers are
  persisted at lookup time, not recovered afterwards; API URLs are stored verbatim; an
  upload-sourced email address is unverified; and the prose-versus-field diff became Gate 7.
- **Added `method/4-research-brief.md`**, which had not previously existed as a document — what a
  research agent collects, how each field is judged, and the three checks it runs before handing
  the file back.
- **Added `selftest/`**: six fabricated contacts and a script that scores them, confirms
  `invariants: clean`, and confirms its refusal guards fire. No network, no credits, one second.
- **Added one scorer guard** (see scorer builds below).

---

## Rubric lineage

Reconstructed from the project's own records. Dates before 3.1.0 are as recorded at the time;
where a record gave only a month, the month is what appears here.

### v3.2 — 2026-09-22 — *Parent control is recorded, not a drop*

Current. Shipped in kit 3.2.0; see that release above for the change and its rationale. Layers
1–3 are unchanged from v3.1, so scores are comparable across the two and routes are not.

### v3.1 — Jul 2026 — *Ownership rules rewritten; disqualified rows keep their scores*

Five changes, all concerning what happens to a lead rather than how it is scored:

1. Strategic parent control disqualifies at **any** deal age, but only on *operational* evidence
   — a careers page or ATS redirecting to the parent, requisitions posted by parent legal
   entities, a domain redirect, a retired brand. Branding-only evidence routes to Review instead.
   This replaced v3.0's 24-month acquisition window, which was wrong in both directions: it
   missed long-settled subsidiaries whose buying genuinely routes through a parent, and it
   dropped companies whose only evidence of absorption was a tagline.
2. Financial-sponsor (PE) ownership is explicitly **not** parent control and is scored normally.
3. **Decentralised serial acquirers** are a third category, scored normally — structurally they
   look like acquisitions, operationally they behave like financial ownership.
4. Geography follows the **contact's** location, not company HQ.
5. A disqualified lead **keeps its real scores**. `route` carries the disqualification. Earlier
   versions zeroed both scores, which destroyed the reviewer's most important input and made a
   genuinely strong prospect display as 0/0.

Layers 1–3 are arithmetically unchanged from v3.0, so **v3.0 and v3.1 rows may be ranked
together** provided `scoring_mode` matches. This is the one documented exception to the
two-axis comparability rule.

The schema gained `route`, `review_reason`, `ownership`, `offshore_check` and `hq_country` in the
same release — without them, the reasoning behind a drop lived only in the run CSV and never
reached the CRM.

### Clarification pass — 2026-07-28 — *no scores changed*

A fresh reading of the rubric found six apparent contradictions, five of them real. Each had the
same cause: a rule whose rationale had never been written down, or a standard written for the
ordinary case and never revisited for an edge case. The offshore rule's justification, the Review
completeness standard for departed contacts, a CRM modifier described but never implemented, the
85-point ceiling on web-only batches, and three conflicting vocabularies for `offshore_check`
were all fixed. **All fixes were to wording, not behaviour, so `rubric_version` stayed `v3.1`.**

### v3.0 — Jul 2026 — *Size floors removed, B2C softened*

A sanity check of the disqualifiers against 50 real won customers found the v2.9 hard floors
would have wrongly excluded **40% of actual wins** (the <5-employee Proven-Fit floor) and **65%**
(the <10-employee Ideal-Fit floor) — the win base is dominated by 1–9-person shops. Size became a
scored criterion, never a gate. B2C became a heavy score penalty rather than an auto-skip, since
real wins exist in consumer-adjacent categories.

### v2.9 and earlier — *superseded*

Hard minimum-employee floors on both scores and a B2C auto-skip; disqualification by 24-month
acquisition window; scores zeroed on disqualification. Superseded in full by v3.0 and v3.1. No
v2.9 scores should be compared against anything current.

### Validation behind the model

A leak-free backtest (41 won deals against 80 Non-Target / Not-Interested losers, scored only on
time-stable fit signals) confirmed the rubric separates winners from losers ~3–4×, established
that persona and company size are the load-bearing signals, and showed the industry list
separates little. That finding is why the weights are what they are and has not been revised.

---

## Scorer builds

| Build | Shipped in | What changed |
|---|---|---|
| **3.2.0 build** | 3.2.0 | Parent control neither disqualifies nor routes; the finding is written to `verdict` and `ownership`, and a new invariant checks it survives. The hedge guard now covers `parent_control_confirmed` as a flatly-stated claim rather than as a disqualifier. |
| **Kit build** | 3.1.0 | Refuses to run on an `email_status` value it does not map, naming the required normalisation, instead of silently scoring it 0 — which cost 4 or 8 Layer 2 points on every row carrying one. Run-specific commentary rewritten as general rules; no arithmetic touched. |
| **Sep 2026, later** | pre-kit | Refuses to run on an empty `competitor`, `distress` or `parent_control_confirmed` judgement, or on one whose opening clause hedges, because the CSV states a disqualification unqualified and would erase the hedge. Establishes up front whether `matched.json` can answer the departure test and stops with a named error rather than answering "this person left" for everyone. Emits a bare `INDEPENDENT` rather than a trailing-colon `INDEPENDENT:`. Reads `li-urls.json` into `li_company`. |
| **Sep 2026, earlier** | pre-kit | Europe and the Middle East score their proper geography band instead of collapsing to 0. Unknown company size scores 0 rather than falling through to the small-company 8. The B2C penalty actually zeroes company type and industry instead of only announcing itself. Unresearched and no-firmographics rows route to Review instead of reading as low scores. `ownership_unknown` became reachable. `route` constrained to its three enum values. The holdout is reserved from the pre-flag population. A Proven-Fit Hot row without a verified email raises a violation rather than being silently retiered. |
| **Jul 2026** | pre-kit | First reusable build: the v3.1 arithmetic, the judgement-file contract, and the invariant validator. |

---

## Changing the method

Change the rubric first, then the scorer, then bump the one version line:

- **The model changed shape** — a new layer, a new score, everything needs rescoring → **major**.
- **Anything that can move a number, a tier, a route or a column** → **minor**. This includes a
  change to routing or recording that leaves the arithmetic untouched, because a reader still
  needs to know which ruleset produced a `route` value. Say in the rubric whether old and new
  rows may still be compared; if they may, that exception has to be written down, not assumed.
- **Nothing about any scored output can change** — documents, wording, packaging, or a guard
  that only refuses malformed input → **patch**.

Then update, in this order: `RUBRIC_SUPPORTED` and `KIT_VERSION` in the scorer, the README
header, and an entry here. On a major or minor bump the scorer's `RUBRIC_SUPPORTED` changes too,
so every run config must be updated deliberately — that is the point.

Never relabel scores to make a version mismatch go away. The scorer exits on one deliberately,
and it exits on a three-digit `rubric_version` for the same reason: the comparability key has to
keep meaning what it says.
