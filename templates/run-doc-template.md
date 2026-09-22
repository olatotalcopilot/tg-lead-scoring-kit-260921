# Scoring run — `<campaign>`

**Date:** · **Rubric:** v3.2 · **Kit:** (the `kit x.y.z` line the scorer prints) ·
**scoring_mode:** · **Source list:** (name, count, distinct companies; any already-scored
carve-out; which source is authoritative if more than one exists)
**Deliverable:** `<csv filename>` (rows, columns)

> Sections marked * are required. They are what makes runs comparable and drops auditable.
> Delete this quote block and every parenthetical instruction before shipping.

## Outcome *

| | count |
|---|---|
| Scored | |
| Work | |
| Review | |
| Disqualified | |
| Hot on both fits, in Work | |

Proven-Fit tiers: Hot · Qualified · Nurture · Skip · Invalid
Ideal-Fit tiers: Hot · Qualified · Nurture · Skip · Invalid

**Disqualifications**, counted per *instance* — a row appears under every reason that fires on
it, which is what a CRM filter will find. Say so when the instance count exceeds the row count.

| Reason | Instances |
|---|---|
| | |

**Review queue by `review_reason`:**

| Reason | count |
|---|---|
| | |

## Gate 5 — did the batch print `invariants: clean`? *

State plainly whether it did. If it did not, list every violation, say why it is acceptable to
ship, and name who decided. A batch that ships past this gate without the reason written here is
not auditable.

## Rule decisions made in this run *

Any judgement call not already covered by the rubric, with the evidence and the case that forced
it. Where a boundary case was decided rather than flagged, say which way and why — those are the
ones someone will want to reverse later. Flag anything here that should be promoted into the
rubric.

## What the Apollo verification pass caught *

Departures, stale records, wrong org names, no-match rows, rows with no firmographics. Be precise
about which flag covers which rows, so nobody works the same problem twice under two names.

## Notable drops *

Every disqualified row scoring Qualified or better — name it and say why it was dropped, so the
decision is auditable rather than invisible. Order by Proven-Fit. Note separately any row that
clears the bar on Ideal-Fit only.

| Proven | Ideal | Company | Reason |
|---|---|---|---|
| | | | |

## Method notes

Anything learned about the tools that would save the next run time or credits.

## Known limitations *

What is NOT verified. Be specific about which rows are affected, and prefer counts to adjectives.
Cover at least:

- rows where research could not run, and why
- rows with no firmographics
- uncorroborated domains, and whether any disqualification rests on one
- offshore ratios that are unmeasurable (`0/0`) rather than a measured negative
- LinkedIn post counts sitting at the 50-post cap, where cadence cannot be compared
- `hiring = 0` rows that are "not found" rather than a verified absence
- what the holdout actually is, and whether it can carry the weight the schema gives it
- blank `li_company` values and which of them are recoverable

## Follow-ups

Job changes to action, personas to retarget, rows awaiting research, decisions awaiting a human.
Number them; this list is what the next run starts from.
