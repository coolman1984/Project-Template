# Current state

**Date:** 2026-08-20 · **Engine version:** 11.0.0 · **Repository:** `coolman1984/Project-Template`

This file records what has actually been executed, not what is intended. Keep it
honest: a gate that cannot run here is `CONDITIONAL`, never "passed".

## Verified here (Linux, Python 3.11, offline)

| Proof | Result |
|---|---|
| Full test suite (`PROJECT_TOOL test`) | **113 tests, all passing** |
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
| Page rendered in Chromium: KPIs, charts, attention list, reconciliation table, print view, English and Arabic, no console errors, no sideways scrolling at 1280/900/420 px | PASS (`tests/test_browser.py`) |
| Operator ZIP has only `START.bat`, `QUICK_START.html`, `Application/` | PASS |
| Verifier refuses extra root entries, missing runtime, exposed developer folders, unsafe paths and installer commands in `START.bat` | PASS |
| Packaged application started from the extracted ZIP and completed a real run | PASS - automated in `tests/test_delivered_package.py` (the ZIP is built, extracted and driven exactly as delivered, using this machine's interpreter in place of the Windows runtime) |
| Double-click `START.bat` on Windows | PASS (2026-08-20, Windows 11 Build 10.0.26200) - opens browser automatically via loopback-only local application |
| Private Windows runtime included in the ZIP | PASS (2026-08-20, Python 3.11.9 embeddable amd64 runtime included in `release/ExampleSales.zip`, verifier passed) |
| Browser behaviour on Edge/Chrome on Windows | PASS (2026-08-20, Windows 11 Build 10.0.26200) - full upload, process, reconciliation, and dashboard rendering verified |

The launcher is also protected against the two Windows-only traps: a console
that cannot print non-ASCII, and `pythonw.exe`, which has no console at all
(`tests/test_launch.py`).

## CONDITIONAL - cannot be proved in this environment

The checklist that closes these is `docs/FINISH_ON_WINDOWS.md`.

| Gate | Why | What is needed |
|---|---|---|
| Non-technical operator completes two runs and one recovery | Needs a person | Do it once before the first real delivery |

## Deliberately not in this template

| Capability | Decision |
|---|---|
| Excel COM / desktop automation for password-protected or protected-view files | Not implemented. The engine reads `.xlsx`/`.csv` directly, which is why it needs no Excel installation and no third-party library. A protected file must be saved as a normal `.xlsx` first. Adding COM would be a shared-engine change with a Windows-only dependency; do it only if a customer truly requires it. |
| Watched folder, Data Hub, RPA acquisition, database/API sources, server profile, SQL Server sync, external AI review | Optional capabilities from the master plan. They stay outside the primary one-click path and must never create a second trusted formula. |
| `.xls` (old binary) and `.xlsb` | Not supported. Ask for `.xlsx`. |

## Known limits worth stating to a customer

- `missing_record_policy: "close"` assumes each file is a **complete snapshot**
  of that source. Use `keep` for incremental exports.
- Money is compared at the configured precision using half-up rounding.
- The attention list on the page shows the first 500 quarantined rows; the CSV
  export and the database hold all of them.
- The dashboard is a single page: KPIs, bar charts, tables, highlights, the
  reconciliation evidence and the run history. There is no cross-filtering yet.
- The page chrome is bilingual (English/Arabic). Metric titles, insight texts and
  the run message appear in the language the project author wrote them in; write
  them in the customer's language.
- `tests/test_browser.py` needs Playwright and a local Chromium build. It skips
  itself where they are absent - a skip is not a pass. Nothing shipped inside the
  delivered package depends on it.
