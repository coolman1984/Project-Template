# What "fully automated" means here

The target behaviour for a recurring report, and exactly which part of this
template does each step. Read the third column before writing any code: almost
every step is already built, and the two or three that are not are deliberate.

```text
📁 A new Excel file appears
        ↓
✅ It is confirmed complete and unchanged
        ↓
📦 It is read in large blocks, never cell by cell
        ↓
🧾 Its structure is checked against what was agreed
        ↓
🗃 Every value is staged with its lineage
        ↓
🧹 Values are typed, checked, and bad rows set aside
        ↓
🕒 New, changed, repeated and missing records are resolved
        ↓
🔒 Trusted history is updated in one transaction
        ↓
🧮 Trusted calculations run in SQL
        ↓
🧊 The figures people filter are pre-aggregated once
        ↓
🔎 Deterministic rules pick out what changed
        ↓
📄 A compact dashboard payload is written
        ↓
🎨 The page - and a self-contained copy of it - is produced
        ↓
✅ The output is verified before anything is published
        ↓
📁 The run is COMPLETE, with all lineage kept
```

## The seventeen steps, and where each one lives

| # | Step | Where it happens | State |
|---|---|---|---|
| 1 | A new source file is detected or selected | `engine/automation.py` watches a folder; the page also accepts files by drag-and-drop | **built** |
| 2 | The pipeline identifies the report type | `project.json` matches each file by name pattern to a source | **built** |
| 3 | The file is confirmed stable and ready | `engine/excel/discovery.py` copies, re-checks size and time, and refuses a file still being written (`E-IN-004`) | **built** |
| 4 | Excel opens it through the approved user session (COM) | *not implemented, on purpose* - see below | **deliberate difference** |
| 5 | The configured worksheet and range are found | `sheet` and `header_row` in the source; missing columns fail as `E-IN-003` | **built** |
| 6 | Data is read in large chunks, never cell by cell | `engine/excel/xlsx_reader.py` streams rows and inserts in batches of 5,000 | **built** |
| 7 | Each chunk is staged safely | `engine/data/staging.py` → `stg__<source>` with file, hash and Excel row number | **built** (SQLite, not DuckDB - see below) |
| 8 | Structure and data quality are checked | `engine/data/clean.py` - typing, seven rule types, quarantine that stays visible | **built** |
| 9 | New, changed, duplicate, historical and snapshot rows are resolved | `engine/data/history.py` - business keys, versions, refused corrections, closures | **built** |
| 10 | Trusted history is updated atomically | `engine/pipeline.py` runs the whole run inside one transaction | **built** |
| 11 | SQL Server is synchronised when available | *not implemented* - an optional connector, never the trusted path | **optional, not started** |
| 12 | Advanced calculations and KPIs run in SQL | `sql/metrics.sql` per project; `engine/data/metrics.py` runs and stores them | **built** |
| 13 | Deterministic insight rules identify important changes | `engine/data/insights.py` plus the `insights` rules in `project.json` | **built** |
| 14 | A compact dashboard payload is generated | `engine/report/dashboard.py` writes `dashboard.json`, including the pre-aggregated cube | **built** |
| 15 | A single self-contained HTML dashboard is compiled | `engine/report/standalone.py` - one file with page, styling, behaviour and data inside | **built** |
| 16 | Automated checks verify the dashboard output | `dashboard.verify` (every displayed KPI equals its calculated value) and `cube.verify` (the cube re-proved against the database) | **built** |
| 17 | The run is marked COMPLETE and all lineage is retained | `runs`, `run_files`, `run_events`, the run manifest and the recovery archive | **built** |

## The differences, and why they exist

### Step 4 - no Excel COM

The engine reads `.xlsx` and `.csv` directly, using only the Python standard
library. That single decision is what makes the delivered package work with
**nothing installed**: no Excel, no pip, no wheels, no drivers, no administrator.

The cost is real and worth stating: a **password-protected or "protected view"**
workbook must be saved as a normal `.xlsx` before the report can read it.

Add COM only if a customer genuinely cannot do that. It is a shared-engine
change that brings a Windows-only dependency (`pywin32`), needs Excel installed
on the machine, and makes the run depend on a desktop session - which a
scheduled run does not have.

### Step 7 - SQLite, not DuckDB

SQLite is part of the Python standard library, so it ships inside the package at
no cost. DuckDB is a very good column store and would be faster on tens of
millions of rows, but it is a separate binary wheel per platform, and the
reports this template targets - a monthly export, a few hundred thousand rows -
run in seconds on SQLite.

This is invisible to everyone except whoever changes the engine. If a customer
genuinely has that much data, it is a contained change: `engine/db/database.py`
is the only module that knows which database is in use.

### Step 11 - no SQL Server synchronisation

Deliberately outside the primary path. The one-click local product must never
depend on a company server being reachable, and a second store must never become
a second trusted formula. If it is added, it publishes *from* the trusted
history after the run has been proved - never into it.

## What "runs daily, weekly or monthly" means in practice

The same files arrive again, with more rows and sometimes corrections. Nothing
special is needed for that - it is what the history layer is for:

- the same file processed twice changes nothing (`0` new records);
- a corrected row becomes version 2 of the same record, not a duplicate;
- a record that disappears is either kept or closed, whichever the business said.

Three ways to make it happen without anyone learning anything:

| How | What to configure | Who starts it |
|---|---|---|
| Drag the file onto the page | nothing | the person |
| Watched folder | `"automation": {"watch_folder": "…", "check_every_minutes": 10}` | the application, while it is open |
| Scheduled | nothing in the project | Windows Task Scheduler calling `Application\runtime\pythonw.exe Application\app\launch.py --run-once` as a standard user |

The scheduled form needs no administrator rights, no service and no console: it
processes whatever is waiting, writes the result, and exits.

## What the person sees at the end

- the dashboard in the browser, with filters, comparisons and the evidence;
- **Save a copy** - one `.html` file containing everything, which opens by
  double-clicking on any machine, with no application and no internet;
- CSV exports of any table or chart;
- the reconciliation table proving the totals, and the run history.
