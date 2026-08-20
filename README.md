# Ultimate Excel Automation V11 — project template

A finished, tested Excel-automation product that a coding agent adapts to one
customer in a short conversation, and delivers as a single offline ZIP that a
non-technical person runs by double-clicking.

```text
Template ZIP + the customer's Excel files + a plain explanation
        ↓   (a chat session: configure, prove, package — do not rebuild)
ProjectName.zip
        ↓
extract → double-click START → the browser opens → add files → Process → trust the numbers
```

**Agent: start at [`PROJECT_SKILL.md`](PROJECT_SKILL.md).**
**Business user: start at [`docs/FOR_THE_BUSINESS_USER.md`](docs/FOR_THE_BUSINESS_USER.md).**

## Why this exists

Rebuilding an Excel pipeline in every chat is slow and expensive, and the result
is different every time. Here the engine is built once and proved by tests. A
session only has to learn *this* customer's files and *this* customer's meaning,
then change configuration and SQL — usually nothing else.

## The two packages, never confused

| Package | Who uses it | What is inside |
|---|---|---|
| `Project-Template.zip` | the adaptation agent | engine, tests, docs, tools, a working example project |
| `ProjectName.zip` | the business user | `START.bat`, `QUICK_START.html`, `Application/` — and nothing else |

Build the first with `python tools/make_template_zip.py`; build the second with
`python PROJECT_TOOL.py deliver`.

## Commands

```bash
python PROJECT_TOOL.py new-project AcmeSales                      # start an adaptation
python PROJECT_TOOL.py doctor  --project projects/AcmeSales       # check the configuration
python PROJECT_TOOL.py run     --project projects/AcmeSales --inbox ./files --verbose
python PROJECT_TOOL.py serve   --project projects/AcmeSales       # open the application
python PROJECT_TOOL.py test                                       # the full suite
python PROJECT_TOOL.py deliver --project projects/AcmeSales --output-dir release \
       --runtime runtime_inputs/python-windows                    # the final ZIP
```

Try it now, with the example project and its safe fixtures:

```bash
python PROJECT_TOOL.py run --project projects/example_sales \
       --inbox projects/example_sales/fixtures --verbose
python PROJECT_TOOL.py serve --project projects/example_sales
```

## What the finished report gives a person

A single page with date-range and dimension filters, period-over-period
comparisons, line / bar / stacked / donut charts, search and sort on every
table, light and dark mode, English and Arabic, CSV exports, and **Save a copy**
— one self-contained `.html` file that opens by double-clicking anywhere, with
no application and no internet.

Filtering never recalculates a trusted number: the engine pre-aggregates the
facts once per run and the browser filters by summing those cells. A run refuses
to publish if that cube disagrees with a second, independent pass over the same
data.

For the whole recurring-report flow — what is built, what is deliberately not —
see [`docs/AUTOMATION_FLOW.md`](docs/AUTOMATION_FLOW.md).

## What the engine does on every run

```text
copy the inputs safely → fingerprint them → read them block by block
→ stage the raw values with lineage → type and check → quarantine the rejects
→ merge trusted history in one transaction → reconcile rows and control totals
→ run the trusted SQL metrics → pre-aggregate what people will filter
→ build evidence-backed highlights
→ verify the dashboard → publish atomically → archive → log
```

A failed run publishes nothing, changes no trusted history, and leaves the last
approved dashboard exactly as it was.

## No dependencies, on purpose

The engine uses only the Python standard library — `zipfile` and `xml` to read
and write `.xlsx`, `sqlite3` for the local database, `http.server` for the
loopback application, and hand-written HTML/CSS/JS with no libraries. That is
what makes the delivered package genuinely offline: it carries the official
Windows embeddable Python and needs no pip, no wheels, no installer and no
administrator rights.

## Repository layout

| Path | What |
|---|---|
| `PROJECT_SKILL.md` | The agent's instructions — read first |
| `.ai/` | Context pack, project map, business questions, current state, report template |
| `docs/` | Product goal, master plan, adaptation guide, configuration reference, packaging, troubleshooting |
| `engine/` | The shared engine (change only with proven evidence) |
| `projects/_template/` | The starting point for a new adaptation |
| `projects/example_sales/` | A complete working example with safe fixtures |
| `tests/` | The proof — 146 tests |
| `tools/` | Fixture generator, template ZIP builder |
| `runtime_inputs/` | Where the private Windows runtime is placed before delivery |

## Finishing it on Windows

The one remaining task before a real delivery — adding the private Windows
runtime and proving the package on a Windows PC — is a checklist in
[`docs/FINISH_ON_WINDOWS.md`](docs/FINISH_ON_WINDOWS.md).

## Status

See [`.ai/CURRENT_STATE.md`](.ai/CURRENT_STATE.md) for exactly what has been
proved and what is still `CONDITIONAL` (anything needing a real Windows machine
or a person). Nothing in this repository is described as release-ready before
those gates pass.
