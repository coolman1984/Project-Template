# AI PROJECT TEMPLATE — ONE GUIDE

## Goal

You receive:

```text
Template ZIP + Excel files + plain business explanation
```

Return:

```text
ProjectName.zip
```

The final user must only:

```text
Extract ZIP → double-click START.bat → browser opens → work offline
```

## Most important rule

**Do not build a new application. Adapt the included reusable engine.**

The template exists to avoid rebuilding Excel handling, validation, history, database, local web app, dashboard shell, offline runtime, packaging, logging, recovery and tests for every project.

## Keep context small

1. Read this file first and treat it as the only human instruction file.
2. Inspect the supplied Excel structure and the small project configuration area.
3. Do not read the whole engine.
4. Search for an engine capability only when the current project cannot be solved by configuration or project-owned logic.
5. Read only the exact engine files required for that proven gap.

Large binaries, runtimes and packaged dependencies are implementation assets, not model context.

## Adaptation order

Always use this order and stop as soon as the requirement is solved:

```text
1. Reuse existing engine capability
2. Change project configuration / Excel mappings
3. Add project-owned SQL
4. Add small isolated project-owned Python only when SQL is unsuitable
5. Change shared engine only when a reusable capability is genuinely missing
```

Normal target: **zero shared-engine changes**.

Never duplicate the engine inside a project. Never replace the application with a workbook, static page or one-off script simply because it is easier to generate.

## Understand the business before coding

From the supplied files and explanation, determine only what is needed for correctness:

- what work is being automated;
- role of each file and sheet;
- what one row represents;
- business key(s);
- how sources relate;
- how corrections, duplicates and missing records should behave;
- which source wins when values disagree;
- trusted row counts or totals used to prove correctness;
- required KPIs, exceptions, filters and outputs;
- what decision the dashboard should support.

Ask the user only for business meaning that cannot be safely determined from the files or explanation. Do not ask technical architecture questions.

Never invent unknown business meaning. Mark it pending until confirmed.

## Build the project

Adapt only the small project-specific area whenever possible:

```text
PROJECT/
  project configuration
  source mappings
  validation rules
  trusted SQL
  optional isolated Python
  dashboard configuration
  focused tests / expected totals
```

The reusable engine and packaged runtime should remain unchanged unless a real reusable gap is proven.

Trusted calculations must have one source of truth. Do not calculate the same KPI independently in SQL, Python, browser code and AI prompts.

## Required verification

Before delivery, prove at minimum:

- original Excel files are unchanged;
- expected files, sheets and columns are validated;
- row counts and trusted totals reconcile;
- duplicate/correction/history behavior matches the business rule;
- identical rerun does not create duplicate trusted records;
- failed processing does not corrupt trusted history or replace the last good result;
- dashboard numbers equal the trusted calculation output;
- the application works with no internet or runtime downloads;
- the final package needs no system Python, Node.js, Git, terminal, administrator rights or package installation;
- final package verification passes.

Do not call a test passed when the current environment cannot actually prove it. State the exact remaining target-PC check instead.

## Final package rule

The non-technical user should see only a simple operator package such as:

```text
ProjectName/
  START.bat
  QUICK_START.html
  Application/
```

Do not expose source code, tests, Git files, dependency caches, migrations, configuration editors, build tools or technical setup choices at the visible root.

## Finish the job

When execution tools are available, do not stop after analysis or a coding plan. Complete the adaptation, run the applicable tests, build the package, verify it and return the finished `ProjectName.zip`.

Final response should be short and state only:

```text
Project: <name>
Business checks: PASS / pending items
Tests and reconciliation: PASS / exact conditional items
Shared engine changed: NO / justified change
Offline package: PASS / exact target-PC check
Output: ProjectName.zip
```
