# Read this first (adaptation agent)

You have received a **template ZIP that is already a finished, tested product**.
Your job is **not** to build an Excel automation system. It exists. Your job is
to point it at this customer's files and return one ZIP.

> Rebuilding any part of this engine is the single most expensive mistake you can
> make here. Everything below exists and is covered by tests: reading .xlsx
> without any library, staging, typing, quality rules, quarantine, exact
> reconciliation, idempotent history, SQL metrics, the local web application,
> the offline package and its verifier.

## The whole job in six steps

1. **Read three files, nothing else** (about 600 lines total):
   - `.ai/CONTEXT_PACK.md` - everything you need to know to adapt this template
   - `.ai/PROJECT_MAP.md` - where each file lives, one line each
   - `projects/example_sales/project.json` - a complete, working example
2. **Ask the business questions** in `.ai/BUSINESS_QUESTIONS.md`. Ask only what
   changes the numbers. Never invent a business meaning; leave it as
   `PENDING_APPROVAL` and say so.
3. **Create the project**: `python PROJECT_TOOL.py new-project <Name>`
4. **Edit exactly two files**:
   - `projects/<name>/project.json` - files, columns, keys, rules, totals, dashboard
   - `projects/<name>/sql/metrics.sql` - the trusted calculations
5. **Prove it**:
   ```
   python PROJECT_TOOL.py doctor --project projects/<name>
   python PROJECT_TOOL.py run    --project projects/<name> --inbox <folder with their Excel files>
   python PROJECT_TOOL.py test
   ```
6. **Deliver one ZIP**:
   ```
   python PROJECT_TOOL.py deliver --project projects/<name> --output-dir release \
       --runtime runtime_inputs/python-windows
   ```
   Give the user `release/<Name>.zip` and nothing else.

## The order you are allowed to work in

```
reuse as-is
→ change project.json
→ change projects/<name>/sql/metrics.sql
→ add isolated project-owned Python (only if SQL cannot express it)
→ change the shared engine (only with proven evidence of a real gap)
```

For an ordinary project the correct number of shared-engine changes is **zero**.
If you are editing anything under `engine/`, stop and re-read this line.

## Never do these

- Never rebuild the pipeline, the Excel reader, the web page or the packager.
- Never add a dependency. The engine is standard-library only, on purpose: that
  is what makes the offline package possible without pip, wheels or installers.
- Never put a business value (a rate, a threshold, a customer name) in `engine/`.
- Never calculate the same trusted number twice - it lives once, in SQL.
- Never approve a business meaning yourself.
- Never hand the user anything but `<Name>.zip`.

## What "done" means

`python PROJECT_TOOL.py deliver ...` prints `RESULT: PASS`, the tests pass, and
the numbers were confirmed by the person who owns them. Write what you did into
`.ai/ADAPTATION_REPORT.md` (copy the template next to it) and hand over the ZIP.
