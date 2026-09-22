# Self-test

Six fabricated contacts and a complete set of intermediates. **No real companies, no real
people, no network calls, no credits.** Every `.test` domain is reserved and resolves nowhere.

```
bash selftest/run-selftest.sh
```

Expected last line: `SELFTEST PASSED`.

Run it once at the start of a scoring run, before spending anything. It proves the scorer is
executable in this environment and that its refusal guards work, and it takes a second.

The fixture deliberately exercises six outcomes:

| Contact | Outcome |
|---|---|
| C1 Acme Consulting | Hot on both scores, verified email, route Work |
| C2 Bridgeway Staffing | Disqualified — competitor (a staffing firm) |
| C3 Offshore Delivery Co | Disqualified — offshore concentration 77.5% |
| C4 Northwind Fabrication | Review — `contact_left_company`; contact scores blank and `Invalid`, **company scores stay real at 82/78** |
| C5 Quietbrook Advisors | Review — `not_researched`; also the batch's `holdout` row |
| C6 Legacy Holdings Group | Snapshot departure caught from employment history |

The script then makes six broken copies and checks the scorer refuses each one: a hedged hard
disqualifier, an empty hard disqualifier, an `email_status` the scorer does not map, a patch
digit in `rubric_version` (which must carry major.minor only), a rubric version the scorer does
not implement, and a `matched.json` that cannot answer the departure test.

The fixture is also the fastest way to see what every pipeline file looks like when it is
correct — read it alongside `scorer/file-formats.md`.
