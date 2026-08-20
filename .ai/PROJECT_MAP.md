# Project map

One line per file, so you never have to search the repository.

## Read these to adapt (that is all)

| File | Why |
|---|---|
| `.ai/CONTEXT_PACK.md` | Every rule, schema and command you need |
| `.ai/BUSINESS_QUESTIONS.md` | What to ask the business owner |
| `projects/example_sales/project.json` | A complete working example to copy |
| `projects/example_sales/sql/metrics.sql` | Example trusted calculations |

## What you edit (project-owned)

| Path | Purpose |
|---|---|
| `projects/<name>/project.json` | The business meaning: sources, columns, keys, rules, totals, dashboard, insights |
| `projects/<name>/sql/metrics.sql` | The trusted whole-report calculations, one SQL query per metric |
| `projects/<name>/sql/fact.sql` | The flat rows the dashboard filters and charts |
| `projects/<name>/tests/golden.json` | Values that must not change silently |
| `projects/<name>/fixtures/` | Small, safe sample files (never real customer data) |

## Shared engine (do not change without proven evidence)

| Path | Responsibility |
|---|---|
| `engine/cli.py` | `PROJECT_TOOL` commands |
| `engine/config.py` | Loads and strictly validates `project.json` |
| `engine/pipeline.py` | The deterministic run order; one transaction per run |
| `engine/paths.py` | Where the database, inbox, logs and archive live |
| `engine/errors.py` | Plain-language errors and the support-code registry |
| `engine/logging_setup.py` | File and console logging |
| `engine/launch.py` | Application entry point used by `START.bat` |
| `engine/excel/xlsx_reader.py` | Dependency-free .xlsx reader (streaming, block based) |
| `engine/excel/xlsx_writer.py` | Dependency-free .xlsx writer (fixtures, exports) |
| `engine/excel/csv_reader.py` | CSV/TSV reader with the same shape |
| `engine/excel/discovery.py` | Finds, hashes and safely copies approved inputs |
| `engine/data/staging.py` | Raw staging with lineage (`stg__<source>`) |
| `engine/data/types.py` | Value parsing and exact money scaling |
| `engine/data/clean.py` | Typing, quality checks, quarantine (`clean__<source>`) |
| `engine/data/history.py` | Idempotent connected history (`hist__<source>`, view `v_<source>`) |
| `engine/data/reconcile.py` | Row population, control totals, relationships |
| `engine/data/metrics.py` | Parses and runs the project SQL metrics |
| `engine/data/cube.py` | Pre-aggregates the facts so the browser can filter by summing |
| `engine/automation.py` | Watched folder and unattended runs |
| `engine/data/insights.py` | Evidence-backed highlights |
| `engine/data/archive.py` | Recovery archive and atomic publishing |
| `engine/db/database.py` | SQLite access, migrations, safe identifiers |
| `engine/db/migrations/*.sql` | Core tables |
| `engine/report/dashboard.py` | Builds and verifies `dashboard.json` |
| `engine/report/standalone.py` | Compiles the self-contained saved copy of the dashboard |
| `engine/webapp/server.py` | Loopback-only local API |
| `engine/webapp/static/*` | The one-page application (HTML, CSS, JS - no libraries) |
| `engine/packaging/builder.py` | Stage A private application, Stage B operator ZIP |
| `engine/packaging/verifier.py` | The gate that enforces the simple ZIP shape |
| `engine/packaging/templates/` | `START.bat` and `QUICK_START.html` |

## Tools and proof

| Path | Purpose |
|---|---|
| `PROJECT_TOOL.py` | Every command an agent runs |
| `tools/make_fixtures.py` | Regenerates the example Excel files |
| `tools/make_template_zip.py` | Rebuilds the template ZIP for the next chat |
| `tests/` | 100+ tests: Excel, config, pipeline, history, recovery, reconciliation, metrics, web, packaging, CLI |
| `runtime_inputs/` | Where the Windows private runtime is placed before delivery |
| `docs/AUTOMATION_FLOW.md` | The recurring-report flow, step by step, and what is deliberately not built |
| `docs/` | Product goal, master plan, configuration reference, packaging, troubleshooting |
