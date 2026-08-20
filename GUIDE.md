# AI PROJECT TEMPLATE — ONE GUIDE

## 1. Product goal

You receive:

```text
Template ZIP + Excel files + plain business explanation
```

You return:

```text
ProjectName.zip
```

The non-technical user only:

```text
Extract ZIP → double-click START.bat → browser opens → work offline
```

This is a reusable recurring-report engine. Do not rebuild the application for every workbook or department.

## 2. Core rule

**Adapt business meaning, mappings and calculations. Reuse the engine.**

The engine already owns:

- file discovery and stability checks;
- normal Excel reading;
- Microsoft Excel COM fallback for protected/NASCA DRM workbooks;
- chunked extraction;
- DuckDB staging and local trusted history;
- schema/data-quality validation;
- duplicate, correction, historical and snapshot handling;
- optional SQL Server synchronization;
- SQL calculation execution;
- deterministic insight rules;
- dashboard dataset/JSON generation;
- modern self-contained HTML dashboard generation;
- run status, lineage, logs and recovery;
- fast automatic verification;
- offline packaging and startup.

Normal target: **zero shared-engine changes**.

## 3. Keep AI context small

1. Read this guide first. It is the only human instruction file.
2. Inspect the supplied Excel files structurally and read `PROJECT/project.json`.
3. Do not read the whole engine.
4. Change only the small project area whenever possible.
5. Search the engine only when the project cannot be implemented through configuration or project SQL.
6. Read only the exact engine file needed for a proven reusable gap.

Large binaries, database engines, frontend assets and packaged dependencies are runtime assets, not model context.

## 4. What the AI normally edits

```text
PROJECT/
  project.json        ← main project definition
  logic.sql           ← optional project calculations
```

A tiny `logic.py` may exist only for a genuinely unsuitable SQL case. Prefer not to use it.

Most projects should require only `project.json` plus `logic.sql`.

`project.json` describes source files, sheets/ranges, keys, history mode, trusted totals, mappings, validation, SQL Server target, KPIs, filters, charts, insights, recurrence and output names.

## 5. Mandatory recurring automation flow

A finished recurring project must follow this pipeline:

```text
New Excel appears or user selects it
↓
Identify project/report type
↓
Confirm the file is stable and ready
↓
Try normal XLSX reading
↓
If protected/NASCA DRM or normal read fails for an authorized workbook:
open through the approved Microsoft Excel COM user session in read-only mode
↓
Discover configured worksheet/table/range
↓
Read data in large chunks — never cell-by-cell
↓
Stage chunks safely in DuckDB
↓
Validate source structure and data quality
↓
Clean and standardize approved fields
↓
Resolve new / changed / duplicate / historical / snapshot rows
↓
Update trusted local history atomically
↓
Synchronize SQL Server when configured and available
↓
Run trusted calculations and KPIs in SQL
↓
Run deterministic insight rules for meaningful changes
↓
Generate dashboard datasets
↓
Generate compact optimized dashboard JSON
↓
Generate one self-contained dashboard.html
↓
Run fast automatic dashboard/data checks
↓
Publish final report atomically
↓
Mark run COMPLETE and retain lineage
```

A failed run must not corrupt trusted history and must not replace the last good dashboard.

## 6. Excel and NASCA DRM rule

Use two automatic paths:

```text
Normal workbook → lightweight XLSX reader
Protected / NASCA DRM workbook → Microsoft Excel COM fallback
```

COM rules:

- use the authorized interactive Windows user session;
- open source workbook read-only;
- allow Excel/NASCA to perform its normal authorization;
- never bypass DRM or security controls;
- discover only the configured data area;
- read rectangular blocks/chunks, never cells one-by-one;
- never save changes to the source workbook;
- restore Excel state and close/release the COM session safely.

If authorization requires user interaction, show one plain-language action and resume the same run afterwards.

## 7. History behaviour

The AI must explicitly choose the correct business behaviour in `project.json`:

```text
append              new immutable business events
upsert              same business key may be corrected
replace_period      a period/file replaces the previous version of that period
snapshot            each run is a dated snapshot
```

Do not invent history behaviour. Infer it only when the business meaning is clear; otherwise ask one concise business question.

Identical input must be idempotent: rerunning it must not duplicate trusted records.

## 8. Trusted calculations

Trusted numbers must be deterministic.

Preferred order:

```text
project.json mappings/rules
→ reusable engine SQL
→ PROJECT/logic.sql
→ tiny isolated project Python only when SQL is unsuitable
→ shared-engine change only for a proven reusable gap
```

A KPI or business formula has one source of truth. Do not independently recalculate the same trusted value in SQL, JavaScript and AI prompts.

AI may explain verified numbers; AI must not invent trusted KPI values.

## 9. SQL Server synchronization

DuckDB is the local/offline working and history layer.

When SQL Server is configured and reachable:

```text
trusted local transaction completes
→ synchronize approved tables/rows
→ record sync status
```

If SQL Server is unavailable, the local run may still complete when the project allows offline operation. Record the pending synchronization and retry later. Never lose the local trusted result because the network database is temporarily unavailable.

## 10. Dashboard engine is already built

Do not design a new web application for every project.

The shared dashboard shell must already provide:

- modern 2026 responsive visual design;
- KPI cards;
- line, bar, area, pie/donut and combination charts;
- tables with sorting/search;
- date, category and multi-select filters/pickers;
- shared cross-filtering;
- drill-down/detail views;
- period comparisons;
- exception/warning views;
- deterministic insights panel;
- run status and last-update information;
- responsive desktop/laptop layout;
- print/export-friendly layout;
- light/dark-ready styling when enabled;
- Arabic/English-ready labels when configured.

The project configuration supplies titles, fields, filters, KPIs, chart definitions and insight rules. The AI should not rebuild HTML/CSS/JavaScript unless the shared dashboard truly lacks a reusable feature.

Output is one self-contained local `dashboard.html` plus its compact data payload, with no internet/CDN dependency.

## 11. Insights

Insights are deterministic rules over verified data, for example:

- largest increase/decrease;
- unusual variance against prior period;
- threshold breach;
- top contributor to movement;
- new exception appearing;
- repeated issue worsening;
- missing expected activity;
- concentration risk;
- trend reversal.

The AI configures these rules for the new business case. It does not generate unsupported conclusions.

## 12. Fast project verification — keep it small

Do **not** run a giant generic test suite for every new Excel project.

The reusable engine is tested separately. Each adapted project only needs these high-value gates:

```text
1. SOURCE      original workbook unchanged
2. STRUCTURE   required sheet/range/columns/types valid
3. RECONCILE   row counts + agreed trusted totals match
4. HISTORY     identical rerun + approved correction behaviour works
5. CALCULATION expected KPI/control examples match
6. OUTPUT      dashboard JSON/HTML builds and contains matching values
```

Add a project-specific test only when it protects a real business risk. Do not create tests merely to increase test count.

Dashboard checks should be automatic and fast: JSON validity, required sections, values reconcile with trusted SQL output, HTML generated, no remote dependencies, and no obvious broken references.

Environment-specific checks such as protected corporate workbook authorization are proven on the authorized target PC and are not repeated unnecessarily for every project.

## 13. Business understanding

From the supplied files and explanation determine:

- what work/report is being automated;
- role of each workbook and sheet;
- what one row represents;
- business keys and source relationships;
- duplicate/correction/missing-record meaning;
- history mode;
- source precedence when values disagree;
- trusted counts/totals used to prove correctness;
- KPIs and calculations;
- exceptions and meaningful-change rules;
- required filters, charts and outputs;
- whether SQL Server synchronization is required;
- daily, weekly, monthly or manual recurrence.

Ask only for missing business meaning that materially affects correctness. Do not ask the non-technical user architecture questions.

## 14. Recurrence

The same finished project must support:

```text
manual selection
or
watched folder / new-file detection
```

and recurrence such as:

```text
daily / weekly / monthly
```

The business logic is configured once. New files reuse the same project definition automatically unless structure drift is detected.

If source structure changes materially, stop safely and report the changed columns/sheets instead of silently producing wrong results.

## 15. Final package

The final non-technical package should expose only:

```text
ProjectName/
  START.bat
  QUICK_START.html
  Application/
```

Normal operation requires no internet, system Python, Node.js, Git, terminal, administrator rights or package installation.

The application should open the browser automatically and expose a simple screen for:

```text
Run / Select File
→ progress
→ PASS / WARNING / BLOCK
→ dashboard
→ history
→ insights
→ export/open report
```

## 16. Finish the job

When execution tools exist, do not stop at a plan. Adapt the project, run the six fast gates, build the offline package and return the finished `ProjectName.zip`.

Final response should remain concise:

```text
Project: <name>
Business checks: PASS / pending meaning
Fast gates: 6/6 PASS / exact conditional item
Shared engine changed: NO / justified reusable change
SQL Server sync: enabled / not used / pending target connection
Offline package: PASS / exact target-PC check
Output: ProjectName.zip
```
