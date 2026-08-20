# START HERE — AI ADAPTATION AGENT

## Your job

You are not building a new application.

You receive:

```text
THIS TEMPLATE
+ Excel files
+ plain business explanation
```

You must return:

```text
ProjectName.zip
```

The final user extracts it, double-clicks `START.bat`, the browser opens, and the application works offline.

## Token-saving rule

Do **not** read the whole repository first.

Read only, in this order:

1. `PRODUCT_GOAL.md`;
2. `.ai/CURRENT_STATE.md`;
3. `.ai/PROJECT_MAP.md`;
4. `.ai/CONTEXT_PACK.md` when present;
5. the exact project/config files routed by the map.

Search before reading. Read the smallest relevant ranges. Do not inspect unrelated engine modules merely to become familiar with them.

## Mandatory adaptation order

Use the first level that can correctly solve the requirement:

```text
1. REUSE EXISTING CAPABILITY
2. CONFIGURE / MAP THE NEW BUSINESS DATA
3. ADD PROJECT-OWNED SQL
4. ADD ISOLATED PROJECT-OWNED PYTHON ONLY WHEN SQL IS UNSUITABLE
5. CHANGE SHARED ENGINE ONLY AFTER A PROVEN REUSABLE GAP
```

Target for an ordinary project: **zero shared-engine changes**.

Never copy the engine into a new report. Never rebuild an existing database, history layer, web app, Excel adapter, runtime, packaging system, dashboard shell, test harness or recovery mechanism because the new workbook looks different.

## Understand business meaning first

Inspect workbook structure without dumping large confidential tables into model context. Confirm only what affects correctness:

- purpose of the automation;
- role of each workbook/sheet;
- meaning of one row;
- business key(s);
- relationships between sources;
- correction/deletion meaning;
- source precedence;
- trusted row counts/totals;
- required KPIs/exceptions;
- decision the dashboard must support;
- run frequency and business approver.

Unknown meaning remains `PENDING_APPROVAL`. Never invent or self-approve business rules.

## Trusted calculation rule

A trusted formula exists once. Prefer:

```text
configuration → reusable SQL → project SQL → isolated project Python → shared-engine change
```

The browser displays verified results. AI explains verified evidence. Neither becomes a second trusted calculation engine.

## Required tests before delivery

At minimum prove:

- input files remain unchanged;
- schema and required fields are validated;
- duplicates/history behave as approved;
- row counts and trusted totals reconcile;
- identical rerun does not create duplicates;
- a failed run preserves trusted history and last-good output;
- dashboard values equal trusted calculation evidence;
- offline package starts without internet, installation, terminal, admin rights or runtime download;
- final ZIP passes `PROJECT_TOOL package verify`.

A conditional environment test is not a pass.

## Final operator package

The visible root must contain only:

```text
ProjectName/
    START.bat
    QUICK_START.html
    Application/
```

Never expose source code, Git, tests, wheelhouses, migrations, configuration editors, package managers or technical setup choices to the final business user.

## Completion behavior

Do the complete adaptation, testing, packaging and verification in the current work session. Do not stop after analysis or a plan when execution tools are available.

Return the verified `ProjectName.zip` plus a concise statement of business approvals, tests/reconciliations, whether shared core changed, and any genuine target-PC acceptance that remains conditional.
