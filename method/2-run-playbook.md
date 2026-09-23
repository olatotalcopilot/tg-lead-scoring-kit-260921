# TG Sales Agency — Lead Scoring Run Playbook

*How to execute a scoring run. Rubric v3.3.*

This is the **how**. It deliberately does not restate the scoring model or the field list — those
live in one place each, and copying them is what causes version drift.

| Document | Owns | Never copy it into |
|---|---|---|
| `method/1-scoring-rubric.md` | What to score, weights, disqualifiers, tiers, routes, review reasons | anywhere |
| `method/3-field-schema.md` | The output columns and their types | anywhere |
| `method/2-run-playbook.md` (this file) | Pipeline, tool methods, gates, output contract | — |
| `method/4-research-brief.md` | What a research agent must collect and record | — |
| `scorer/TG-score-batch.py` | The scoring arithmetic, as executable code | — |

If any two disagree, **the rubric wins** and the other is the bug.

---

## 0. Where things live

Three distinct places. Keeping them straight matters, because only some of them are durable and
only some are visible to the team.

- **This kit folder.** The method: rubric, playbook, schema, research brief, scorer, templates
  and a self-test. It is read-only input to a run. Nothing a run produces is written back into
  it.
- **The run folder.** One per run, created outside this kit, in the location the person running
  the batch nominates. Everything a run produces goes here. Layout in §5.
- **The agent's working sandbox.** Scratch. Discarded when the session ends. Everything worth
  keeping must be written to the run folder before finishing.

Nothing syncs on its own. **Each session starts from nothing** — access to the person's machine
is granted per session and must be requested again every run, and the scorer is not on the
agent's disk until it is copied out of this kit.

---

## 1. Inputs to confirm before spending anything

Ask for these explicitly and confirm them back before any tool call that costs money.

1. **The batch.** An Apollo saved list (get the name; the list id is in its URL and appears in
   every exported row's `label_ids`), a CSV or spreadsheet export, or explicit contact ids.
   Confirm the count back. If more than one source exists, ask which is authoritative and record
   the answer — a workbook and an Apollo list of the same campaign will not agree.
2. **Tools.** Apollo (required), web search and fetch (required), RapidAPI *Fresh LinkedIn
   Profile Data* (recommended). Without RapidAPI the whole batch is
   `scoring_mode = scored without Linkedin API access` and cannot be ranked against
   LinkedIn-scored batches. That is a whole-batch decision, never a per-row one.
3. **Campaign name** — the join key across Apollo and the CRM, e.g. `2026-08_GA-Founders`. One
   value for the whole batch.
4. **Where the run folder goes**, and whether results should also be copied anywhere else.
5. **Budgets** — Apollo credits and RapidAPI tier. Know what actually consumes Apollo credits:
   **reveals** (email, phone) and **org enrichment**. Matching does not — `apollo_people_match`
   returns full firmographics free **for contacts already revealed to your team**. So a
   saved-list batch, where everything is already revealed, can score end to end at zero, while a
   batch of net-new prospects pays reveals for the same number of rows. Which case you are in
   depends on the list *and* on the team's plan and permissions — confirm it, don't assume it.
   Credit spend is **expected and sanctioned** at one point: the rubric's order of operations
   ends *"only then consider credit-spending enrichment for high scorers still missing emails."*
   What is anomalous is spending **before** scoring, or spending **org-enrichment** credits at
   all — see §3 for why those are almost never needed.

---

## 2. Pipeline

Each stage writes a file the next stage reads. Keep the file contracts stable;
`scorer/TG-score-batch.py` depends on them, and `scorer/file-formats.md` is the authority on
columns.

```
Apollo list export ─→ roster.csv
                        │
        people-match ─→ matched.json ─→ verified.csv
                        │
     offshore screen ─→ offshore.json
                        │
   web + LinkedIn    ─→ research.txt  (+ li-urls.json)
                        │
   human judgement   ─→ judgments.json
                        │
                   TG-score-batch.py --config run-config.json
                        │
                        └─→ TG-scored-full-<campaign>-<rubric>.csv
```

**`roster.csv`** — the raw list export. Remember what it is: a **Contact snapshot** copied into
the workspace on the day the list was saved, not live data. See the rubric's *The saved list is
a snapshot, not live data*.

**`matched.json`** — the **raw** `apollo_people_match` responses, **keyed by `person_id`**, with
`employment_history` intact. This contract is load-bearing, not bookkeeping: the scorer reads
employment history from it to detect departures, that cannot be reconstructed from a flattened
CSV, and a flattened file makes the departure test answer "left the company" for everyone. The
scorer checks up front whether the file can answer the question and stops with a named error
rather than guessing. Do not flatten it before it hits disk, and make sure `roster.csv` carries
the `person_id` the file is keyed on.

**`verified.csv`** — the flattened match result. This is the live view and it wins over the
roster on every field except where the roster is the only source (phone, LinkedIn URL, list
membership).

**`offshore.json`** — `{domain: {num, den, pct, verdict}}`, verdict ∈ `PASS` / `REVIEW` /
`DISQUALIFY`. Where a ratio is not measurable, annotate it — a `0/0` reads like a clean pass and
is actually an absence of data.

**`research.txt`** — one pipe-delimited line per domain, 19 fields. One line per *domain*, not
per contact: company-level research is shared by every contact there.

**`li-urls.json`** — `{domain: {url, source}}`, the company LinkedIn page URL for each domain.
Optional but expected; without it `li_company` ships empty on every row, and the scorer says so.

**`judgments.json`** — every human call in the run, in one file: which companies are
parent-controlled and on what evidence, which are PE-backed, which are competitors, which
contacts have moved. **This is the only file that should differ run to run.** Keys are documented
in the scorer's `JUDGEMENT_KEYS`; an unknown key is a hard error rather than a silent no-op.

**`run-config.json`** — `{campaign, score_date, rubric_version, scoring_mode, source_list,
paths{}}`.

Do **not** hand-write the scoring logic. If a rule needs to change, change the rubric and then
the scorer, and bump `rubric_version`.

---

## 3. Tool methods that are not obvious

These are the difference between a run costing nothing and a run costing credits and hours.

### Apollo

- **`apollo_people_match` returns full firmographics for free** on contacts already revealed to
  your team — employee count, revenue, industry, employment history, verified email. **Org
  enrichment is almost never needed.** Do not spend a credit per company to read
  `owned_by_organization`; a full batch can and should run at zero.
- **Need a company's firmographics but the contact's own match came back empty?** Match *any*
  other employee found via people-search. Free, and it returns the full organization block.
- **Offshore screen — 2 calls per domain, not 8.** `person_locations` accepts multiple countries
  in one call and **unions** them. So: one call with `q_organization_domains_list=[domain]`,
  `per_page=1`, read `total_entries` for the denominator; one more with the same plus all seven
  offshore countries for the numerator. Always `per_page=1` — you want the count, not the people.
  This uses Apollo's **indexed-employee sample**, a directional estimate rather than exact
  headcount. **Small-sample guard:** near the threshold with fewer than ~15 indexed employees,
  route to Review rather than auto-dropping.
- **Do not batch multiple domains into one offshore query.** The totals cannot be attributed back
  to individual companies.
- **Outreach-capability probe** (separate from the concentration screen, and recorded rather than
  routed). Two free calls: the domain plus `person_titles` = `[sales development representative,
  business development representative, account executive, business development, lead generation,
  inside sales]`, `per_page=1` for the denominator; the same plus `person_locations` = the
  **broad low-cost-region list** (the seven offshore countries *plus* Latin America and Eastern
  Europe) for the numerator. Use the broad list — an offshore-only filter is blind to the only
  shape of case ever found. Location must be a *filter*, not a readout: Apollo returns
  `has_country` as a boolean, never the value. Result goes in `verdict`.
- **Apollo org names are unreliable in isolation.** Score on the domain; confirm the name by
  research. Never use name comparison to detect job changes — use employment history.
- **Never fall back to an email-keyed match without checking the returned name.** Apollo returns
  whoever it associates with the address. A name mismatch is no match.
- **A `person_id` minted in the same period as your Contact ids** is a workspace-created record
  with no live People entry. It cannot match by identifier and should not be forced by email.
  Route to Review.
- **A null `organization` on a people-match is usually a departure**, not a missing field. The
  scorer handles this; do not override it without checking employment history.

### RapidAPI Fresh LinkedIn

- `get-company-by-domain` (1 credit) is the universal gate — if there is no page, Layer 3B
  legitimately scores low and you stop there.
- **`get-company-by-domain` must never be trusted as a negative.** It falsely reports "no
  LinkedIn page" often enough that every miss has turned out to have a live page on retry.
  **Always retry with `get-company-by-URL` before recording "no page"**, and never let a blank
  LinkedIn URL be read as evidence that a company has no page.
- `get-company-posts` (2 credits) is **page-capped at 50 posts**, so the post window reflects one
  page, not lifetime cadence. Where a row sits at exactly 50, `li_posts` and the date range are
  floors and cadence cannot be compared across such rows. Say so in the run doc.
- The posts endpoint exposes **no job-slot count**, so `li_hire` is scored from post content
  only. A company with live LinkedIn requisitions but no hiring *posts* scores low there even
  when the web hiring signal is 10. That is expected; note it rather than reconciling it.
- Budget ~2–3 credits per surviving company. Not-found lookups are not charged.
- Rate limit is roughly 2–3 calls per minute in practice. **Pace the agent** rather than letting
  a 429 be recorded as a zero.
- The posts response is large. Parse it to `{date, likes, comments}` in code — never read it into
  the conversation.
- **Persist the identifiers a lookup returns, not only the metric you scored.** The company
  LinkedIn URL comes back in the same response as the follower count, from both Apollo's
  people-match organization block and RapidAPI's company lookups. Save it to `li-urls.json` at
  the moment of the lookup. Recovering URLs afterwards costs credits and a pass that should never
  have been needed.

### Web research

- Web catches self-hosted job postings that LinkedIn's job count misses. Treat the two as
  complementary; neither replaces the other.
- When the search budget runs out, "nothing found" is **not** a verified negative. Mark those
  rows explicitly.
- **Anything harvested from free text must be verified against the source, not merely parsed
  from it.** URL harvesting fails in both directions: a strict pattern silently misses URLs
  written in plain text, and stripping trailing punctuation destroys slugs that legitimately end
  in a period. Both failures look valid from the outside.
- **Do not normalise a URL the API returned.** Store it verbatim, trailing slash included.
  Legitimate LinkedIn slugs end in a period, end in a hyphen, contain an unescaped `&`, use a
  `/school/` path, or bear no resemblance to the company domain. A well-meaning cleanup breaks
  them.

---

## 4. Gates

Each of these exists because skipping it cost something real. Do not pass one silently.

1. **Pilot 5 first.** Run five contacts end to end — enrich, score, write the CSV, mark in Apollo
   — and get sign-off before touching the rest. Catches schema and permission problems on 5
   records instead of 200.
2. **Corroborate a domain before screening on it.** Confirming the *contact* does not confirm the
   *domain*; they are separate fields. The scorer flags an email-domain mismatch automatically
   and routes to Review. Clear a false positive once by adding the domain to
   `judgments.json → domain_confirmed` with what you checked. **Never run the offshore screen or
   Layer 3 on an uncorroborated domain** — a ratio measured for the wrong company looks like
   evidence. A domain that resolves to a different company entirely can flip a row from
   Qualified to a 70%-offshore drop, or the reverse.
3. **Reserve the holdout before applying Review flags.** `eval_group = holdout` is a sample of
   low scorers retained so the model can be measured forward. If flags are applied first, every
   low scorer ends up in Review or Disqualified and the holdout comes out empty. The scorer
   assigns `eval_group` from the pre-flag population and warns if the holdout is empty; do not
   ship past that warning without a decision. Note also what the holdout currently *is*: every
   unworked low scorer, not a random sample, which makes it a weak control — see the README's
   roadmap.
4. **Confirm before any credit spend**, with the count and the cost.
5. **The scorer validates its own output — `invariants: clean` must appear before you ship.**
   It asserts the rubric's rules over the finished rows: no sentinel zeros, tiers follow their
   score, `review_reason` only on Review rows, `route` and `eval_group` inside their enums,
   `ownership` present wherever research ran, no caveat contradicting its own row, and no
   Proven-Fit Hot row without a verified email (the scorer caps those at Qualified, so this
   should only ever fire on a row re-tiered by hand). A violation means the output disagrees with
   the method, which is a stop condition — fix it, or state in the run doc why it is acceptable and
   ship the violation visibly rather than silencing it. This exists because rules written in
   prose do not bind rows written by hand: hand-authored and overridden rows bypass every branch
   in the scorer.
6. **Never zero a score to record a disqualification.** `route` carries that. A zeroed score
   destroys the reviewer's most important input and hides good companies.
7. **Run the prose-versus-field diff before scoring, in both directions.** A research note that
   asserts a call the structured field does not carry means the call never reaches the scorer —
   the scorer reads disqualifiers from `judgments.json`, never from a note, so a competitor call
   made only in prose ships the company as Work. The reverse is just as bad: a field populated
   with a fetch failure, a bare `1`, or text that hedges or contradicts itself ships a named
   company an unqualified allegation. Diff every structured field against its note, both ways,
   and resolve every disagreement before running the scorer.

---

## 5. Output contract

### Run folder

Named `run-YYMMDDctHHMM` (creation date, Central time), created outside this kit.

```
run-YYMMDDctHHMM/
  TG-scored-full-<campaign>-<rubric>.csv   the deliverable, CRM-ready
  TG-run-<campaign>.md                     the run doc (templates/run-doc-template.md)
  TG-score-batch.py                        the scorer, copied in as run
  run-config.json                          settings for this run
  judgments.json                           every human call made
  intermediates/
    roster.csv  verified.csv  matched.json  offshore.json  research.txt  li-urls.json
```

Copying the scorer into the run folder is deliberate: the run stays reproducible even after the
canonical scorer in this kit moves on.

### Naming

`TG-` prefix, hyphens, lowercase words, proper nouns keep their case
(`TG-run-2026-09-GA-Founders.md`). Scripts and pipeline inputs keep snake_case, because they are
referenced by name in code.

---

## 6. Failure modes to guard against

| Symptom | Cause | Guard |
|---|---|---|
| A great company scores 0/0 | A disqualifier zeroed the score | Never zero; `route` records it |
| Offshore ratio measured for the wrong company | Uncorroborated domain | Gate 2 |
| "Not researched" row that is really a departure | Null `organization` read as a data gap | The scorer's snapshot rule |
| Every contact reads as departed | `matched.json` flattened or keyed by `contact_id` | Keep the raw responses keyed by `person_id`; the scorer stops if it cannot answer |
| Holdout empty | Review flags applied before reserving it | Gate 3 |
| Two rubric copies drift apart | Method embedded in a prompt | This kit references, never restates |
| 21 job changes, 5 real | Org-name comparison | Use employment history |
| A subsidiary with its own sales team is dropped | Parent control treated as a disqualifier | The rubric's parent-control finding: record it, work the lead |
| A named company carries a disqualification nobody made | Hedged or empty evidence in a structured field | Gate 7, plus the scorer's refusal to run on hedged evidence |
| A competitor ships as Work | The call was made in a note and never written to the field | Gate 7 |
| "No LinkedIn page" that has one | `get-company-by-domain` false negative | Always retry by URL |
| A working LinkedIn URL turns into a 404 | Trailing punctuation stripped from a valid slug | Store API values verbatim |
