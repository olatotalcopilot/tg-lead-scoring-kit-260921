# Pipeline file formats

The scorer reads seven files. These contracts are load-bearing — the scorer indexes by position
and by exact key name, and several of its safety checks only work when a file honours its
contract. Build the files to this spec, not to whatever an export happens to produce.

All paths are relative to the run folder and are declared in `run-config.json → paths`.

---

## `run-config.json`

```json
{
  "campaign": "2026-09_GA-Founders",
  "score_date": "2026-09-21",
  "rubric_version": "v3.3",
  "scoring_mode": "fully scored",
  "source_list": "the exact file or Apollo list this batch came from, with counts",
  "paths": {
    "roster":    "intermediates/roster.csv",
    "verified":  "intermediates/verified.csv",
    "matched":   "intermediates/matched.json",
    "offshore":  "intermediates/offshore.json",
    "research":  "intermediates/research.txt",
    "li_urls":   "intermediates/li-urls.json",
    "judgments": "judgments.json"
  }
}
```

`scoring_mode` is `fully scored` or `scored without Linkedin API access` — one value for the whole
batch. `rubric_version` must match the version the scorer implements, **major.minor only** — a
third digit is the kit patch level and is refused, because it would split one comparable
population in two. Otherwise the scorer exits rather than silently relabelling scores.

---

## `roster.csv` — the source list, as exported

One row per contact. A point-in-time **Contact snapshot**, not live data.

Required columns, exactly these names:

```
contact_id, person_id, first, last, title, company, domain, website,
li_company, li_person, email, email_status, direct_phone,
city, state, country, org_id, account_id, created, label_ids, founded
```

`contact_id` is the join key to `verified.csv` and to the `judgments.json` contact-level keys.
**`person_id` must be populated** — it is the key `matched.json` is looked up by, and a blank one
disables the departure test.

---

## `verified.csv` — the Apollo people-match pass, flattened

One row per contact that was matched. This is the **live** view and it wins over the roster on
every field except those the roster alone carries (phone, LinkedIn profile URL, list membership).

Required columns:

```
contact_id, person_id, new_title, new_company, domain, emp, rev,
industry, country, email, email_status, seniority, hq_country
```

- `domain` — the **live** company domain. Leave blank when the live record has none; the scorer
  reads a blank against a populated roster domain as a possible departure and handles it.
- `emp`, `rev` — numbers or blank. Blank `emp` scores Size 0 and routes the row to Review as
  `firmographics_unavailable`.
- `country` — the **contact's** country, which is what geography is scored on.
- `hq_country` — the company's HQ country. Recorded, never scored.
- `seniority` — Apollo's value: `c_suite`, `founder`, `owner`, `vp`, `head`, `director`, etc.
- `email_status` — one of `verified`, `unverified`, `extrapolated`, `likely to engage`,
  `unavailable`, or blank. **Normalise before writing this file.** An address supplied on an
  uploaded workbook rather than validated by Apollo — Apollo reports these as
  `email_true_status = "User Managed"` — maps to `unverified`. The scorer stops on any value it
  does not recognise rather than scoring it 0.

---

## `matched.json` — the raw people-match responses

```json
{ "<person_id>": { "...the raw people_match response...",
                   "employment_history": [ {"organization_name": "...",
                                            "start_date": "...", "end_date": null } ] } }
```

**Keyed by `person_id`, with `employment_history` intact.** This is not bookkeeping. The scorer
uses it for the snapshot-vs-live departure test, which cannot be reconstructed from a flattened
file — and a flattened file would make that test answer "this person has left" for every contact,
silently and in the dangerous direction. The scorer checks up front whether the file can answer
the question at all, and stops with a named error the moment a row needs an answer it cannot give.

Match on the **company name** in the history, not on Apollo's `current` flag, which is unreliable.

---

## `offshore.json` — the concentration screen

```json
{ "example.com": { "num": 1, "den": 75, "pct": 1.3, "verdict": "PASS" } }
```

`verdict` ∈ `PASS` / `REVIEW` / `DISQUALIFY` — those three strings only. One entry per domain
screened; a domain absent from this file routes its rows to Review.

Where `den` is 0 the ratio is unmeasurable: it renders as `0/0 = 0.0% (PASS)`, which reads like a
clean pass and is actually an absence of data. Annotate those entries so the run doc can name
them.

---

## `research.txt` — Layer 3, one line per domain

Pipe-delimited, **19 fields in this exact order**, no header row:

```
domain|acq|acq_detail|distress|competitor|hiring|web|ticket|growth|messy|followers|posts|range|median|li_mkt|li_growth|li_hire|note|urls
```

| # | Field | Type | Notes |
|---|---|---|---|
| 1 | `domain` | text | The corroborated domain. Must match the live domain in `verified.csv`. |
| 2 | `acq` | enum | `INDEPENDENT` / `PE_BACKED` / `SERIAL_ACQUIRER` / `ACQUIRED_RECENT` / `ACQUIRED_OLD` / `SUBSIDIARY` / `UNKNOWN` |
| 3 | `acq_detail` | text | Ownership evidence. Where nothing was found, say what was looked at. |
| 4 | `distress` | text | Empty, or a plain assertion. Hard disqualifier. |
| 5 | `competitor` | text | Empty, or a plain assertion. Hard disqualifier. |
| 6 | `hiring` | int 0–10 | |
| 7 | `web` | int 0–5 | |
| 8 | `ticket` | int 0–5 | A 5 here also sets Proven-Fit company type to 12 unless overridden. |
| 9 | `growth` | int 0–5 | |
| 10 | `messy` | int 0–5 | |
| 11 | `followers` | text | May be blank. |
| 12 | `posts` | text | May be blank. Capped at 50 by the API. |
| 13 | `range` | text | The post date window. A floor when `posts` is 50. |
| 14 | `median` | text | Median reactions per post. |
| 15 | `li_mkt` | int 0–10 | |
| 16 | `li_growth` | int 0–3 | |
| 17 | `li_hire` | int 0–2 | |
| 18 | `note` | text | The human-readable verdict. Goes into the CSV's `verdict` column on non-disqualified rows. |
| 19 | `urls` | text | Semicolon-separated evidence links. |

No pipes and no newlines inside any field. The eight integer fields are never blank.

A domain that has an `offshore.json` entry but **no** line here routes its rows to Review as
`not_researched` — an unresearched total is not a score.

---

## `li-urls.json` — company LinkedIn pages

```json
{ "example.com": { "url": "https://www.linkedin.com/company/example-inc/", "source": "Get_Company_by_Domain" } }
```

Optional. If the file is absent the scorer says so and `li_company` ships empty on every row —
which is a missing file, not evidence that these companies have no LinkedIn page.

Store every URL **verbatim as the API returned it**, trailing slash included. Do not strip
trailing punctuation: real slugs end in a period, end in a hyphen, contain an unescaped `&`, or
use a `/school/` path.

---

## `judgments.json` — every human call in the run

The only file that should differ from one run to the next. Keys are validated: an unknown key is
a hard error, not a silent no-op.

| Key | Keyed by | Effect |
|---|---|---|
| `parent_control_confirmed` | domain | Operational evidence the parent runs hiring/procurement/web presence. **Neither disqualifies nor routes** — recorded in `ownership` and stated at the front of `verdict`. |
| `parent_control_inferred` | domain | Branding evidence only. Same treatment, worded as the weaker claim it is. |
| `serial_acquirer` | domain | Decentralised permanent holder. Scored normally. |
| `pe_recent` | domain | Financial sponsor, recap within ~18 months → Review. |
| `pe_backed` | domain | Financial sponsor, older. Scored normally; recorded in `ownership`. |
| `distress` | domain | Hard disqualifier. |
| `competitor` | domain | Hard disqualifier. |
| `b2c` | domain | Heavy score penalty — company type and industry both score 0. Not a disqualifier. Cannot be combined with a `ctype_override` or `ind_override` on the same domain. |
| `left` | contact_id | The contact has left; your note beats the generic snapshot message. |
| `unverifiable` | contact_id | The person cannot be placed at this company by any key. Distinct from `left`. |
| `mismatch_review` | contact_id | List, Apollo and web disagree on employer. |
| `name_fix` | domain | Corrected company name, because Apollo org names are unreliable. |
| `domain_confirmed` | domain | Clears a `DOMAIN NOT CORROBORATED` flag. Record who checked and what they found. |
| `ctype_override` | domain | int 0–12. Overrides Proven-Fit company type. |
| `ind_override` | domain | int 0–10. Overrides Ideal-Fit industry. |
| `row_overrides` | contact_id | `{column: value}`. Last-resort hand corrections; say why in `record_caveats`. Column names are validated against the output schema. |

**`competitor`, `distress` and `parent_control_confirmed` must assert, not hedge.** The scorer
refuses to run on an empty value, or on one whose opening clause contains a word like "possible",
"potential", "appears" or "unclear" — the CSV states each of these unqualified, so a hedge would
be erased and a named company would carry a claim nobody made. `parent_control_inferred` is
exempt: it is worded as the weaker claim, so a qualified reading of it is honest. That check is a
tripwire for the obvious cases, not a proof: a hedge buried deep in a long entry still passes, so
read the entries too.

---

## Output

`TG-scored-full-<campaign>-<rubric_version>.csv`, written to the working directory, sorted by
Proven-Fit then Ideal-Fit descending. Roughly 60 columns; see `method/3-field-schema.md` for what
is canonical, what is carried through and what is a run diagnostic.

The scorer prints, in order: any `NOTE:` lines, then `invariants: clean` **or** a numbered list of
violations, then the row count and the route / review_reason / tier distributions, then a warning
if the holdout is empty. **`invariants: clean` must appear before the batch ships**, or the reason
it did not must be written into the run doc.
