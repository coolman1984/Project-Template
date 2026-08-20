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

The final user only:

```text
Extract ZIP → double-click START.bat → browser opens → work offline
```

## Core rule

**Do not build a new application. Adapt the included reusable engine.**

The engine already owns Excel handling, validation, history, database, local web app, dashboard shell, offline runtime, packaging, logging, recovery and tests.

## Keep AI context small

1. Read only this guide first.
2. Inspect the supplied Excel structure and `PROJECT/project.json`.
3. Do not read or explain the whole engine.
4. Search inside the engine only when `project.json` or project-owned logic cannot solve a proven requirement.
5. Read only the exact engine files needed for that gap.

Large runtimes and packaged dependencies are assets, not model context.

## What you should normally edit

```text
PROJECT/
  project.json        ← main project definition, mappings, rules, dashboard and expected totals
  logic.sql           ← optional, only for project-specific calculations
  logic.py            ← optional, only when SQL is unsuitable
```

Most projects should require only `project.json`.

The build layer converts this small project definition into whatever internal engine configuration is required. Do not force the user or the AI to manage many internal configuration files.

## Adaptation order

```text
1. Reuse existing capability
2. Change PROJECT/project.json
3. Add PROJECT/logic.sql only if needed
4. Add small PROJECT/logic.py only if SQL is unsuitable
5. Change shared engine only when a reusable capability is genuinely missing
```

Normal target: **zero shared-engine changes**.

Never duplicate or rebuild the engine. Never replace the finished application with a workbook, static page or one-off script just because that is easier to generate.

## Understand the business

Determine from the files and explanation:

- what work is being automated;
- role of each workbook/sheet;
- what one row represents;
- business key(s) and source relationships;
- duplicate, correction and missing-record behavior;
- source precedence when values disagree;
- trusted row counts/totals used to prove correctness;
- required KPIs, exceptions, filters and outputs;
- what decision the dashboard supports.

Ask only for missing business meaning that cannot be safely determined. Do not ask technical architecture questions. Never invent an unknown business rule.

## Trusted calculations

A trusted calculation must have one source of truth.

Prefer:

```text
project.json → logic.sql → logic.py → shared-engine change
```

Do not calculate the same KPI independently in SQL, Python, browser code and AI prompts.

## Required verification

Before delivery prove at minimum:

- original Excel files remain unchanged;
- expected files, sheets and columns are validated;
- row counts and trusted totals reconcile;
- duplicate/correction/history behavior matches the approved rule;
- identical rerun creates no duplicate trusted records;
- failure preserves trusted history and last-good output;
- dashboard numbers equal trusted calculation output;
- package works without internet or runtime downloads;
- no system Python, Node.js, Git, terminal, administrator rights or installation is required;
- final package verification passes.

If the current environment cannot prove a target-PC test, state that exact test as conditional. Never pretend it passed.

## Final package

The non-technical user should see only:

```text
ProjectName/
  START.bat
  QUICK_START.html
  Application/
```

No source code, tests, Git files, dependency caches, migrations, configuration editors or technical setup choices at the visible root.

## Finish the job

When execution tools exist, complete the adaptation, tests, build and verification in the same work session. Return the finished `ProjectName.zip`, not merely a plan.

Final response:

```text
Project: <name>
Business checks: PASS / pending items
Tests: PASS / exact conditional items
Shared engine changed: NO / justified change
Offline package: PASS / exact target-PC check
Output: ProjectName.zip
```
