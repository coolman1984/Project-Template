# Project Template

A reusable Excel-to-offline-web-app template for non-technical users.

## The only workflow that matters

```text
Project-Template.zip
+ Excel files
+ plain business explanation
        ↓
AI adaptation agent
        ↓
ProjectName.zip
        ↓
Extract → double-click START.bat → browser opens → work offline
```

The AI must adapt the existing engine, not rebuild the application for every department.

## Why this exists

Building the same database, Excel handling, validation, history, local web app, offline runtime, packaging, tests and recovery again for every automation wastes tokens, time and creates new bugs. This repository builds that technical foundation once and keeps new projects focused on business meaning, mappings and the smallest necessary project logic.

## AI adaptation rule

Use this order and stop at the first level that solves the requirement:

1. reuse the existing capability;
2. change project configuration/mappings;
3. add project-owned SQL;
4. add isolated project-owned Python only when SQL is unsuitable;
5. change shared engine code only when a reusable gap is proven.

An ordinary project should make **zero shared-engine changes**.

## What the non-technical user provides

- the template ZIP;
- the Excel files to automate;
- a plain explanation of the work, important totals, KPIs and expected result.

The agent asks only questions required to make the business result correct.

## What the non-technical user receives

```text
ProjectName/
    START.bat
    QUICK_START.html
    Application/
```

No installation. No terminal. No Git. No package manager. No system Python or Node.js. No runtime downloads. No administrator rights.

## Important status rule

A source repository is not the same thing as a commissioned master ZIP. The reusable engine can be tested in source, but the final `MASTER_TEMPLATE.zip` must also contain the sealed Windows runtime and pass its archive verifier before it is described as ready for repeated cloud adaptation.

Start with `00_START_HERE_AI_AGENT.md` when adapting the template. Do not broad-read the repository unless the project map proves it is necessary.
