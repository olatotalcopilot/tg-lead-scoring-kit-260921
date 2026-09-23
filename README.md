# TG Lead Scoring Kit — read this first

Everything needed to score a batch of prospects for TG Sales Agency the same way every time. You
do not have to read the method — an AI agent reads it for you and asks you for the few things
only you can supply.

---

## Start here — five steps

**1. Download the kit and unzip it.** You want a folder with `AGENT-START-HERE.md` inside it,
next to `method/`, `scorer/`, `templates/` and `selftest/`. Downloading from the repo names the
folder something like `tg-lead-scoring-kit-…-main` — that is fine, leave the name alone.

**2. Open a Claude session that has a connected folder.** Either start a new project and connect
a folder to it, or open an existing session where a folder is already connected. The agent needs
somewhere on your computer it can read from and write to.

**3. Move the unzipped folder into that connected folder.** Keep it whole — the files reference
each other by name, so a loose file on its own will not work.

**4. Check your tools are connected.** Apollo and web search are required. The RapidAPI *Fresh
LinkedIn Profile Data* feed is strongly recommended; without it the whole batch is scored web-only
and cannot be compared against batches that had it.

**5. Paste this into the session:**

```
You are running a lead scoring batch for TG Sales Agency using our existing, validated method.

The method is in the lead scoring kit folder in this session's connected folder — find the
folder that contains AGENT-START-HERE.md next to method/, scorer/ and selftest/, whatever it is
named. Open its AGENT-START-HERE.md and follow it exactly, starting at Step 0.

Do not design a scoring method, write a rubric, or write a scorer — all three already exist in
that folder. Read them first, run the self-test, then tell me what you need from me and wait.
```

**What happens next.** The agent reads the method, runs a one-second self-test that costs
nothing, and comes back asking for your list, a campaign name, where the results should go and
what your budget is. It confirms the contact count and the expected credit spend before it spends
anything. Then it runs the batch — pausing after the first five contacts for your sign-off — and
hands back a CRM-ready spreadsheet plus a written record of what it did and what it could not
verify.

**If something looks wrong**, the rest of this page explains what the kit does and where each
answer lives. You can also just ask the agent — it is told where every answer is.

---

| | |
|---|---|
| **Version** | **3.3.0** |
| **Released** | 2026-09-23 |
| **Title** | Title banding, industry map, Hot needs an email |
| **Description** | The complete scoring method — rubric, playbook, schema, research brief, scorer and self-test — as one self-contained folder a teammate's agent can run from cold. |
| **Stamped on every row** | `rubric_version = v3.3` — **not** comparable with v3.1 or v3.2 scores |

**One version line covers the kit and the rubric.** They used to be numbered separately; they
are not separate things, so they are now the same number.

| Digit | Bumped when | Reaches the data? |
|---|---|---|
| **major** | The model changes shape — a new layer, a new score. Everything needs rescoring. | yes |
| **minor** | Anything that *can* change a number, a tier, a route or a column on some row. | yes |
| **patch** | Nothing about any scored output can change: documents, wording, packaging, or a guard that only refuses malformed input. | **no** |

Only `major.minor` is written into a row. `rubric_version` is a comparability key — the rule is
"filter on `rubric_version` **and** `scoring_mode` before ranking anything" — so equality on it
has to mean *these rows are comparable*. A patch bump cannot change a score by definition, so
letting it through would split one comparable population in two for no reason. The scorer refuses
a config carrying three digits and says so. The kit version is printed when a batch is scored and
belongs in the run doc.

Full lineage of the kit, the rubric and the scorer in [`VERSION-HISTORY.md`](VERSION-HISTORY.md).

---

## The problem it solves

Prospecting used to be inconsistent: the lead-search tool and the CRM held half the picture
each, there was no shared definition of a "good" lead, and effort leaked into poor-fit or
already-dead records. This kit is the agreed definition, written down and executable, so two
people running two batches produce numbers that mean the same thing.

## How it scores

Every lead gets **two scores out of 100**, because TG's real wins and TG's stated ICP are
different companies:

- **Proven-Fit** — how much this lead looks like the customers TG has actually closed:
  founder-led, sub-50-employee service businesses buying $5–12K engagements.
- **Ideal-Fit** — how well it matches the ICP sheet: 51–500 employees, $10–100M revenue, the
  target industry list.

Leads hot on both are priority one. Hot on one only routes to a different play. Keeping them
separate is the point — a single score would hide the gap.

Each score is built from four layers: **fit** (40 pts, the only part that differs between the
two scores), **reachability** (15), **research signals** from the web and LinkedIn (45), and
**CRM history**, which sits beside the score and never moves it, because CRM labels have proved
unreliable.

Separately, a short list of **hard disqualifiers** removes leads that cannot or will not buy: no
web presence, a competitor, visible distress, or a workforce concentrated offshore. A company
owned by a parent is **not** dropped — that finding is recorded in the row and the lead is worked,
because a subsidiary with its own sales team still has a budget it can spend. A disqualified lead
**keeps its real scores** — the `route` column records the drop, so nothing is hidden and a
decision can be reversed.

Every row comes out with a route — **Work**, **Review** or **Disqualified** — and a plain-English
`verdict` saying why, so a rep or a reviewer never has to reconstruct the reasoning.

## What you have to supply

Five things. The agent will ask for all of them up front and confirm the numbers back before
spending anything.

1. **The list** — an Apollo saved list, a CSV or a spreadsheet. If two sources exist for the same
   campaign, say which one wins.
2. **A campaign name**, e.g. `2026-09_GA-Founders`. It is the key that ties the batch together
   across systems.
3. **Which tools are connected** — Apollo and web search are required; the RapidAPI LinkedIn
   feed is strongly recommended. Without it the whole batch is scored web-only and cannot be
   compared against batches that had it.
4. **Where the results should go.**
5. **The budget** — Apollo credits and the RapidAPI tier.

**On cost:** looking a contact up in Apollo is free and returns full company data, so a list of
contacts your team has already revealed can score end to end for nothing. A list of brand-new
prospects pays a credit per reveal. RapidAPI runs about 2–3 credits per company. The dominant
cost is usually the AI research itself, which is controlled by which model the research agents
run on — put bulk research on a cheap tier and reserve the expensive one for synthesis.

## What you get back

A **run folder**, separate from this kit:

- **`TG-scored-full-<campaign>-v3.3.csv`** — the deliverable. One row per contact, ~60 columns:
  both scores, both tiers, company-level scores, the route, the reason, the evidence links, and
  every input that fed the score.
- **`TG-run-<campaign>.md`** — the run doc. Counts by route, every disqualification with its
  reason, every good lead that was dropped and why, what was *not* verified, and what needs a
  human decision. This is what makes a drop auditable six months later.
- **The scorer, the config, the judgement calls and the intermediate files**, so the run can be
  reproduced exactly.

---

## What is in this folder

| File | What it is | Who reads it |
|---|---|---|
| `README.md` | This page | You |
| `VERSION-HISTORY.md` | What changed in each kit release, and the rubric and scorer lineage behind it | You, when a score looks different from last time |
| `AGENT-START-HERE.md` | The entry point. Tells the agent what to read, what to ask you for, how to run the batch and how to answer your questions about it | The agent, first |
| `method/1-scoring-rubric.md` | **The rubric.** What is scored, the weights, the disqualifiers, the tiers, the routes, the review reasons. The final authority — if any other file disagrees with it, the other file is wrong | The agent; you, if you want to know why a lead scored what it did |
| `method/2-run-playbook.md` | How a run executes: the pipeline, the non-obvious tool techniques that keep a run free, the seven gates, and the output contract | The agent |
| `method/3-field-schema.md` | Every output column, its type and its allowed values — and the 23 custom fields to create in Apollo and the CRM so scores can be written back | The agent; whoever sets up the CRM fields |
| `method/4-research-brief.md` | What a research agent must collect for each company and exactly how to record it | The agent, and any sub-agent it delegates research to |
| `scorer/TG-score-batch.py` | The scorer. Implements the rubric's arithmetic, checks its own output against the rubric's rules, and refuses to run on evidence that is empty, hedged or malformed | The agent runs it; nobody edits it per run |
| `scorer/file-formats.md` | The exact contract for every file the scorer reads | The agent |
| `scorer/run-config.example.json` | A filled-in example of the run's settings | The agent |
| `scorer/judgments.example.json` | A filled-in example of the human-judgement file — **the only file that changes from one run to the next** | The agent; you, when you overrule something |
| `templates/run-doc-template.md` | The run-doc skeleton, so every run is written up the same way | The agent |
| `selftest/` | Six fabricated contacts and a one-second check that the scorer works and its safety guards fire. No real data, no network, no credits | The agent, before every run |

**The division of labour matters.** The rubric holds the rules, the scorer holds the arithmetic,
and `judgments.json` holds the human calls for one batch. Nothing is ever copied between them —
copying is what makes two versions drift apart and produce numbers that quietly stop meaning the
same thing.

---

## Known gaps and roadmap

Written down because a method you can trust is one whose weak points are named. Nothing here
blocks a run; all of it is worth knowing before you read a number too confidently.

### Known gaps in the method

1. **Parent-controlled leads have not been measured yet.** As of 3.2.0 they are worked rather
   than dropped, which is the right call on the evidence — one such company closed at several
   times TG's median deal after the old rule would have discarded it — but nobody yet knows what
   share of them reply "that goes through our parent now." Worth counting after a batch or two.
2. **`crm_status` is never populated.** Every row ships `none`, because nothing in the pipeline
   feeds CRM history in. The column is in the schema and the rubric treats it as advisory, but
   until a CRM source is wired the pursue/suppress signal it is meant to carry is simply absent.
3. **The holdout is not a random sample.** It is every unworked low scorer, which means the
   low-score control is weak and forward validation of the research layer has not really begun.
   The fix is to reserve the holdout by random sample before routing.
4. **The industry map is incomplete.** Apollo's taxonomy is larger than the ICP lists, so an
   unrecognised industry still takes the off-list 8. The scorer now names every unmapped string
   it met with a row count, so the gap is visible per run rather than silent — but mapping the
   full taxonomy is still outstanding.
5. **The `domain` column shows the source list's domain, not the one that was scored.** Where
   the live lookup resolved a different domain, that is what the ratio and the research were
   measured on, and a reader of the spreadsheet cannot tell.
6. **Subjective reviewer signals are not systematised.** Judgements like "the CEO seems settled"
   or "the website looks local" are re-made per lead rather than encoded as a rule that binds
   every run. The same is true of the boundary of the competitor rule and of the unassessed
   industries — they are one problem, not three.
7. **"Callable" is an axis the model does not score.** Reviewers reliably flag companies as
   exciting to call — good site, active people, real market presence — and those markers are
   close to the *inverse* of the Proven-Fit thesis, which rewards a founder still carrying
   revenue and marketing that is not landing. The model measures need and reachability, not
   whether there is a live conversation to walk into. One of the two instincts is wrong and it
   is cheap to find out which.
8. **Manager-level titles are excluded when the list is built, but the rubric still scores
   them 4.** Both behaviours are defensible; having them undocumented in the same system is not.
9. **Two LinkedIn bands genuinely overlap.** A large firm can post consistently, draw engagement
   below ~0.3% of followers, and still get dozens of reactions per post — satisfying both the
   "trying but not landing" 10 and the "real traction" 6. The research brief requires the reading
   to be stated; it does not yet pick one.
10. **LinkedIn hiring is scored from post content only**, because the endpoint exposes no job
    count. A company with live requisitions and no hiring posts scores low there.
11. **A hiring score of 0 usually means "not found", not "verified absent"** — only the research
    note distinguishes them, and no column does.

### Roadmap

| # | Item | Why it matters |
|---|---|---|
| 1 | **Re-examine parent-control drops in batches scored before 3.2.0.** They were disqualified under a rule that no longer exists; each is a Qualified-or-better lead sitting in a CSV | A cheap query against CSVs already held. Sizes what the old rule cost, and puts recoverable leads back in play |
| 2 | **Wire a CRM source into `crm_status`**, so the advisory column carries something | Today the pursue/suppress signal the rubric describes never reaches a row |
| 3 | Reserve the holdout by random sample before routing | Makes forward validation of the research layer possible at all |
| 4 | Encode the subjective judgements, the competitor-rule boundary and the unassessed industries as rules | One workstream, not three tickets; ends the per-run re-decision |
| 5 | Emit the resolved live domain alongside the source-list domain | Lets a spreadsheet reader see which company was actually measured |
| 6 | Run the "exciting to call" tag experiment on a batch's Work rows and compare conversion against equally-scored rows | Cheapest available test of whether the model or the reviewer is right |
| 7 | **Write-back.** Create the 23 shared custom fields in Apollo and the CRM so scores land where reps work | Turns the method into infrastructure rather than a spreadsheet. Blocked on an admin creating the fields once; until then, named lists plus the CSV are the workaround |
| 8 | **Reconcile the two databases** into one matched, deduped source of truth | Must come before any full-scale run, or the same company gets scored twice across unaligned systems |
| 9 | **Full run** across all funnel survivors, plus a recurring refresh | Data decays; stale records produce wrong buyers and missed job changes |

### How to change the method

Change the rubric first, then the scorer, then bump `rubric_version` — and never the other way
round. Scores are only comparable within a version, and a change that alters the arithmetic makes
old and new batches incomparable. A change that only alters routing or recording does not.

Record every reviewer ruling somewhere durable the day it is made. A ruling that lives only in a
chat thread is lost when the thread scrolls, and the next run re-decides it from scratch.
