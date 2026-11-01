# Notes

## Q1 2026 net income

Net income for 2026-01-01 to 2026-03-31 is **-44,480.14** (a net loss).

```
Total revenue                    37,850.50
Cost of goods sold              (14,272.75)
Gross profit                     23,577.75
Total operating expenses        (68,100.07)
Operating income                (44,522.32)
Other income (interest)              42.18
Net income                      (44,480.14)
```

## Decisions and assumptions

- Only `posted` entries count. Drafts (JE-019) and voids (JE-009, JE-025) are ignored.
- Dates are inclusive. `start == end` is allowed, future dates give zeros, and entries need not be in date order (JE-007).
- Invalid dates, or start after end, return HTTP 422 and the page shows the message.
- Revenue is credit minus debit and expense is debit minus credit, so contra revenue (4900) and the Software credit (JE-020) reduce their totals. Only revenue and expense accounts appear.
- Entries are reported as recorded. Rent (JE-007) is not re-accrued, and only the recognized deferred revenue counts (3 x 1,000, not the 12,000 billed).
- Inactive account 6300 appears because it has posted history. Accounts with no activity show 0.00.
- When every amount is zero the page still shows the full table, with a neutral note ("All amounts are zero for this period") and no error. It does not say "no posted entries", because a posted entry can touch only balance sheet accounts (JE-013).
- Gross profit, operating income and net income are calculated rows. Every other section shows its accounts and a total.
- Money is exact: `Decimal` in the backend, strings in the API, and the page only formats them.
- The ledger is checked at startup (known status and accounts, balanced entries), so a bad file stops the server with a clear message.

## How I checked the numbers

- Worked out Q1, February, March, 2026-03-31, December and April by hand.
- Recalculated every line from the raw JSON with exact fractions (a different method) for 1,128 date ranges. All matched.
- 54 tests cover each data trap, the real ledger, the API errors and the startup checks. One recomputes Q1 net income from the raw entries.
- Broke the code on purpose (flipped signs, counted drafts, off-by-one dates) and confirmed tests failed.
- Ran the page in Chrome with a script: loading, Search, Quick select, errors, an empty range, a backend outage and layout.

## Where AI helped, and where it was wrong

AI wrote the calculation, tests and page, which I reshaped over many rounds. I checked every number myself.

- My first deliberate-bug run said two sign flips passed. The check was flawed (it matched a docstring and Python used cached bytecode). I reran it and both were caught.
- AI set `alignItems` on MUI `Stack` as a prop, which this version ignores silently. I noticed in the browser and moved it into `sx`.
- AI hard-coded the company name. I pointed out it must follow the ledger.
- AI's edit for the calculated rows missed one spot after a reformat. The tests caught it.
- Converting to a float before `Decimal` still passed the tests (results are rounded to cents), so the exact-money tests do not catch every float mistake.

## What I would do next

- Charts and margin percentages (with `Decimal`).
- Click an amount to see its journal entries.
- A database, with reload without a restart.
