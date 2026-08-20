# Current state

**Date:** 2026-08-20 · **Engine version:** 11.0.0 · **Repository:** `coolman1984/Project-Template`

This file records what has actually been executed, not what is intended. Keep it
honest: a gate that cannot run here is `CONDITIONAL`, never "passed".

## Verified here (Linux, Python 3.11, offline)

| Proof | Result |
|---|---|
| Full test suite (`PROJECT_TOOL test`) | **146 tests, all passing** |
| Golden run on the example fixtures | `WARNING` (2 rows quarantined by design), KPIs match `projects/example_sales/tests/golden.json` |
| Control totals reconcile exactly | PASS (integer minor units, difference `0.00`) |
| Every row accounted for (accepted / rejected / out of scope) | PASS, and a deliberately deleted row is detected as `BLOCK` |
| Identical rerun creates no duplicates | PASS (0 new, 121 unchanged) |
| Late correction updates the same record to version 2 | PASS |
| Refused correction keeps the trusted value and stays visible | PASS |
| Failed run keeps the previous dashboard and history untouched | PASS (missing column, missing file, too many bad rows, unapproved meaning) |
| Recovery archive restores a previous published result | PASS |
| Local application: upload → process → dashboard → CSV export | PASS |
| Loopback only, session key enforced, traversal refused | PASS |
| No page asset references the internet | PASS (asserted in `tests/test_webapp.py`, and re-checked in a real browser: zero external requests) |
| Page rendered in Chromium: KPIs, four charts, attention list, reconciliation table, print view, English and Arabic, dark mode, no console errors, no sideways scrolling at 1280/900/420 px | PASS (`tests/test_browser.py`) |
| Filtering equals what the database answers for the same question | PASS - every dimension value and every period cross-checked against SQL (`tests/test_analytics.py`), and re-checked in the browser: Wholesale reads 122,297.00 in the page and in the database |
| A cube that lost a row is refused before publishing | PASS |
| The saved copy opens from `file://` with no server: same numbers, filters still work, zero network requests | PASS (`tests/test_standalone.py`, plus a Chromium run) |
| Watched folder notices a changed file once, and an unchanged file never | PASS (`tests/test_automation.py`) |
| `launch.py --run-once` processes and exits with a status code | PASS |
| Operator ZIP has only `START.bat`, `QUICK_START.html`, `Application/` | PASS |
| Verifier refuses extra root entries, missing runtime, exposed developer folders, unsafe paths and installer commands in `START.bat` | PASS |
| Packaged application started from the extracted ZIP and completed a real run | PASS - automated in `tests/test_delivered_package.py` (the ZIP is built, extracted and driven exactly as delivered, using this machine's interpreter in place of the Windows runtime) |
| Double-click `START.bat` on Windows | PASS (2026-08-20, Windows 11 Build 10.0.26200) - opens browser automatically via loopback-only local application |
| Private Windows runtime included in the ZIP | PASS (2026-08-20, Python 3.11.9 embeddable amd64 runtime included in `release/ExampleSales.zip`, verifier passed) |
| The example run on Windows produced the agreed numbers | PASS (2026-08-20) - `WARNING`, 124/121/2/1 rows, total 298,944.47, 55 invoices, average 5,435.35, 12 customers; every reconciliation check `PASS` except the expected `link_to_customers` `WARNING` |
| A second run on Windows with the network switched off | PASS (2026-08-20) - same totals, 0 new records, 121 unchanged |
| `PROJECT_TOOL deliver` on Windows | PASS (2026-08-20) - `RESULT: PASS`, 77 entries, private runtime included |

The launcher is also protected against the two Windows-only traps: a console
that cannot print non-ASCII, and `pythonw.exe`, which has no console at all
(`tests/test_launch.py`).

## CONDITIONAL - cannot be proved in this environment

The checklist that closes these is `docs/FINISH_ON_WINDOWS.md`.

| Gate | Why | What is needed |
|---|---|---|
| Non-technical operator completes two runs and one recovery | Needs a person | Do it once before the first real delivery |
| A person looking at the rendered page in Edge or Chrome on Windows | The Windows verification drove the application through its own local API, and read the numbers from it | Open the page once on Windows and look at it. The rendering itself is covered by `tests/test_browser.py` in Chromium |

## Deliberately not in this template

| Capability | Decision |
|---|---|
| Excel COM / desktop automation for password-protected or protected-view files | Not implemented (step 4 of `docs/AUTOMATION_FLOW.md`). The engine reads `.xlsx`/`.csv` directly, which is why it needs no Excel installation and no third-party library. A protected file must be saved as a normal `.xlsx` first. Adding COM would be a shared-engine change with a Windows-only dependency; do it only if a customer truly requires it. |
| DuckDB in place of SQLite | Not adopted. SQLite ships inside the standard library, so it costs the package nothing; DuckDB is a per-platform binary wheel and only pays off at tens of millions of rows. `engine/db/database.py` is the only module that would change. |
| SQL Server synchronisation, Data Hub, RPA acquisition, database/API sources, server profile, external AI review | Optional capabilities from the master plan. They stay outside the primary one-click path and must never create a second trusted formula. |
| `.xls` (old binary) and `.xlsb` | Not supported. Ask for `.xlsx`. |

## Known limits worth stating to a customer

- `missing_record_policy: "close"` assumes each file is a **complete snapshot**
  of that source. Use `keep` for incremental exports.
- Money is compared at the configured precision using half-up rounding.
- The attention list on the page shows the first 500 quarantined rows; the CSV
  export and the database hold all of them.
- Charts carry at most four series; anything beyond folds into "Other". The
  colour palette is validated for four hues in both light and dark mode, and a
  fifth would not be reliably distinguishable.
- A dimension with more than 12 distinct values still groups charts, but is not
  offered as filter chips - a wall of chips is not a filter.
- Distinct counts are whole-report figures and cannot be filtered; the page
  labels them so nobody reads a filtered figure that is not filtered.
- The page chrome is bilingual (English/Arabic): headings, buttons, table
  headers and the file area switch with the العربية button. Everything the
  **engine** writes is English only - the run message, the progress steps, the
  built-in highlights, the reasons rows were rejected, and every error message.
  **This is a decision taken on 2026-08-20 by the product owner, not an
  oversight: do not translate the engine's messages unless asked to.**
  Text the **project author** writes (metric titles, chart titles, insight
  wording, the purpose line) appears exactly as written - write those in the
  customer's language.
- Every value written into the page carries `dir="auto"`, so an English sentence
  inside an Arabic page keeps its punctuation at the correct end. The browser
  test asserts this; do not remove it.
- `tests/test_browser.py` needs Playwright and a local Chromium build. It skips
  itself where they are absent - a skip is not a pass. Nothing shipped inside the
  delivered package depends on it.
