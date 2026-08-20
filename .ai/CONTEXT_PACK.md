# Context pack

Everything needed to adapt this template. If it is not here, you almost
certainly do not need it.

---

## 1. What already exists

| Capability | Where | Status |
|---|---|---|
| Read .xlsx without any third-party library | `engine/excel/xlsx_reader.py` | done, tested |
| Read CSV/TSV | `engine/excel/csv_reader.py` | done, tested |
| Find, hash and copy inputs without touching the originals | `engine/excel/discovery.py` | done, tested |
| Raw staging with lineage | `engine/data/staging.py` | done, tested |
| Typing, quality rules, quarantine | `engine/data/clean.py` | done, tested |
| Idempotent history with corrections and closures | `engine/data/history.py` | done, tested |
| Exact reconciliation (rows and control totals) | `engine/data/reconcile.py` | done, tested |
| Trusted SQL metrics | `engine/data/metrics.py` | done, tested |
| Evidence-backed insights | `engine/data/insights.py` | done, tested |
| Recovery archive, atomic publish | `engine/data/archive.py` | done, tested |
| One-page bilingual web application | `engine/webapp/` | done, tested |
| Offline operator ZIP + verifier | `engine/packaging/` | done, tested |

**You add none of this. You configure it.**

---

## 2. The run order (already implemented)

```
copy inputs safely → fingerprint → read → stage raw with lineage
→ type and check → quarantine rejects → merge trusted history (transaction)
→ reconcile rows and totals → run SQL metrics → build insights
→ verify the dashboard → publish atomically → archive → log
```

The whole run is one SQLite transaction. A failed run changes nothing and leaves
the last approved dashboard in place. Statuses: `PASS`, `WARNING`, `BLOCK`.

---

## 3. `project.json` - the file you spend most of your time in

```jsonc
{
  "project_name": "AcmeSales",              // no spaces; becomes the ZIP name
  "title": {"en": "Sales performance", "ar": "أداء المبيعات"},
  "language": "en",                          // page language on first open
  "approval": {                              // the business owner's confirmation
    "status": "APPROVED",                    // APPROVED | PENDING_APPROVAL
    "approved_by": "Name", "approved_on": "2026-08-19", "notes": ""
  },
  "business": {
    "purpose": "...", "decision_supported": "...", "run_frequency": "monthly"
  },
  "sources": [ /* see 3.1 */ ],
  "relationships": [ /* see 3.2 */ ],
  "metrics_sql": "sql/metrics.sql",
  "dashboard": {                             // omit to show every metric automatically
    "kpis": ["total_amount"],
    "charts": [{"metric": "amount_by_month", "chart": "bar"}],
    "tables": ["top_customers"]
  },
  "insights": [ /* see 3.3 */ ],
  "quality_gates": {
    "block_on_reconciliation_failure": true, // stop rather than publish wrong totals
    "max_rejected_percent": 20,              // stop if too many rows fail the rules
    "archive_keep_runs": 10
  }
}
```

Unknown or misspelled keys fail immediately with the exact path - trust the
error message instead of guessing.

### 3.1 A source

```jsonc
{
  "id": "sales",                     // letters/digits/underscore; becomes a table name
  "title": "Monthly sales export",   // what the user calls this file
  "match": ["sales_*.xlsx"],         // file name patterns the user will drop in
  "format": "xlsx",                  // xlsx | csv
  "sheet": "Sales",                  // tab name, index, or null for the first tab
  "header_row": 1,                   // the Excel row holding the headings
  "delimiter": null,                 // csv only; null = detect
  "required": true,                  // false = the run may proceed without this file
  "grain": "One row is one invoice line.",
  "business_key": ["invoice_no", "line_no"],   // what identifies the same record
  "corrections_allowed": true,       // may a later file change an existing record?
  "missing_record_policy": "keep",   // keep | close  (close only for full snapshots)
  "columns": [
    {"source": "Invoice No",     // the heading EXACTLY as it appears in Excel
     "field": "invoice_no",      // the internal name used in SQL
     "type": "text",             // text | number | integer | date | datetime | boolean
     "required": true,           // empty value -> the row goes to quarantine
     "trim": true,
     "default": null,
     "date_formats": ["%d/%m/%Y"]}   // optional hint when a date is ambiguous
  ],
  "filters": [                       // rows the business considers out of scope
    {"field": "status", "operator": "not_equals", "value": "Cancelled"}
  ],
  "checks": [ /* see 3.4 */ ],
  "control_totals": [{"field": "amount", "precision": 2, "tolerance": "0"}]
}
```

Filter operators: `equals`, `not_equals`, `in`, `not_in`, `not_null`.

Filtered rows are recorded, not forgotten: reconciliation proves that every row
read is either accepted, rejected or deliberately out of scope.

### 3.2 A relationship

```jsonc
{"child": "sales", "child_fields": ["customer_id"],
 "parent": "customers", "parent_fields": ["customer_id"],
 "on_missing": "warn"}      // warn | block | ignore
```

### 3.3 An insight rule

```jsonc
{"id": "small_average_invoice",
 "when": {"metric": "average_invoice_value", "operator": "<", "value": 500},
 "severity": "watch",                       // info | watch | action
 "title": "Average invoice value is low",
 "body": "The average invoice is {value}, below the 500 review threshold."}
```

`{value}`, `{threshold}` and any KPI id can be used in the text. Insights may
only repeat what a metric proved.

### 3.4 Checks

| type | fields it uses | what it means |
|---|---|---|
| `not_null` | `field` | the value must be present |
| `not_blank` | `field` | present and not only spaces |
| `unique` | `fields` | no two rows may share these values |
| `range` | `field`, `min`, `max` | numeric bounds |
| `allowed_values` | `field`, `values` | a fixed list |
| `regex` | `field`, `pattern` | full-match pattern |
| `not_future` | `field` | a date may not be after today |

Each check takes `"on_fail"`: `quarantine` (default - the row is set aside and
stays visible), `warn` (kept, but listed) or `block` (stop the whole run), plus
an optional `"message"` and `"next_action"` in plain language.

---

## 4. `sql/metrics.sql` - the trusted calculations

```sql
-- metric: total_amount
-- kind: kpi
-- title: Total revenue
-- format: money
-- unit: SAR
SELECT ROUND(SUM(amount), 2) AS value FROM v_sales;

-- metric: amount_by_month
-- kind: series
-- title: Revenue by month
-- format: money
SELECT substr(invoice_date, 1, 7) AS label, ROUND(SUM(amount), 2) AS value
FROM v_sales GROUP BY 1 ORDER BY 1;

-- metric: top_customers
-- kind: table
-- title: Top customers
SELECT c.customer_name AS "Customer", ROUND(SUM(s.amount), 2) AS "Revenue"
FROM v_sales s LEFT JOIN v_customers c ON c.customer_id = s.customer_id
GROUP BY 1 ORDER BY 2 DESC LIMIT 10;
```

Rules:

- read `v_<source_id>` (active trusted records). Never `stg__` or `clean__`.
- `kind: kpi` returns one row with a `value` column;
  `kind: series` returns `label` and `value` (optionally `series`);
  `kind: table` returns any columns - the headings are shown as written.
- `format`: `money`, `integer`, `percent` or `number`. Formatting is display
  only; the stored number is what was proved.
- `title` is shown exactly as you write it, in both languages. Write metric and
  chart titles in the customer's own language - the engine's own messages stay
  in English by decision (see `.ai/CURRENT_STATE.md`).
- Only `SELECT`/`WITH` is allowed. A metric can never modify data.
- Dates are stored as `YYYY-MM-DD` text, so `substr(date, 1, 7)` is the month
  and normal string comparison works.

Extra columns available on every view: `record_key`, `record_version`,
`record_status`, `first_run`, `last_run`.

---

## 5. Commands

```bash
python PROJECT_TOOL.py new-project AcmeSales
python PROJECT_TOOL.py doctor  --project projects/AcmeSales
python PROJECT_TOOL.py run     --project projects/AcmeSales --inbox ./their_files --verbose
python PROJECT_TOOL.py serve   --project projects/AcmeSales          # opens the browser
python PROJECT_TOOL.py test
python PROJECT_TOOL.py deliver --project projects/AcmeSales --output-dir release \
       --runtime runtime_inputs/python-windows
python PROJECT_TOOL.py package verify --zip release/AcmeSales.zip
```

`doctor` is cheap and catches almost every mistake before a run. Use it after
every edit to `project.json`.

Add `--allow-unapproved` to `run` while the business owner has not confirmed the
meaning yet. Never add it to a delivery.

---

## 6. Support codes (shown to the user, logged for you)

| Code | Meaning |
|---|---|
| `E-CFG-001..004` | The project configuration is missing, invalid or has an unknown setting |
| `E-CFG-005` | The business meaning is not approved yet |
| `E-IN-001` | A required input file was not provided |
| `E-IN-002` | A file could not be opened, or the tab does not exist |
| `E-IN-003` | A required column is missing from the file |
| `E-IN-004` | The file changed while it was being read |
| `E-VAL-001` | Too many rows failed the agreed rules |
| `E-REC-001` | Totals did not reconcile - nothing was published |
| `E-HIST-001` | Trusted history could not be updated |
| `E-SQL-001` | A project calculation failed |
| `E-PKG-001` | The delivered package does not have the approved shape |
| `E-RUN-001` | The run stopped unexpectedly; previous results were kept |

---

## 7. The two packages

| Package | For | Contents |
|---|---|---|
| `Project-Template.zip` | you, in a chat | engine, tests, docs, tools, example project |
| `<Name>.zip` | the business user | `START.bat`, `QUICK_START.html`, `Application/` |

The operator ZIP is verified automatically. It fails if anything else is visible
at its root, if the private runtime is missing, or if `START.bat` would install,
download or elevate anything.

---

## 8. Delivering a runtime the user does not install

The engine uses only the Python standard library, so the private runtime is just
the official **Windows embeddable package** unzipped into
`runtime_inputs/python-windows/` before you run `deliver`. No pip, no wheels, no
virtual environment, no admin rights. See `docs/OPERATOR_PACKAGE.md`.

If you cannot obtain it (for example the chat has no network access), deliver
with `--allow-missing-runtime`, and say plainly in your handover that the ZIP is
**not yet runnable on a clean machine** and needs the runtime added. Do not call
it finished.
