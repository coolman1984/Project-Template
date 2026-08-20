# `project.json` reference

The complete list of settings. The validator rejects anything not listed here,
naming the exact path, so a typo costs one line of output rather than a run.

## Root

| Key | Type | Required | Meaning |
|---|---|---|---|
| `project_name` | string | yes | Internal name; becomes `<name>.zip`. Letters, digits, `_`, `-`. |
| `title` | object or string | no | `{"en": "...", "ar": "..."}`; shown on the page. |
| `language` | string | no | `en` or `ar`; the language the page opens in. |
| `approval` | object | no | `status` (`APPROVED` / `PENDING_APPROVAL`), `approved_by`, `approved_on`, `notes`. A run refuses to publish unless the status is `APPROVED`. |
| `business` | object | no | `purpose`, `decision_supported`, `run_frequency`. Shown to the user and recorded in the run manifest. |
| `sources` | array | yes | One entry per input file. |
| `relationships` | array | no | How sources join. |
| `metrics_sql` | string | no | Path to the metrics file, default `sql/metrics.sql`. |
| `dashboard` | object | no | Which metrics appear as KPIs, charts and tables, and in what order. Omit to show everything. |
| `insights` | array | no | Rules that turn a metric into a highlight. |
| `quality_gates` | object | no | `block_on_reconciliation_failure` (default `true`), `max_rejected_percent` (default `100`), `archive_keep_runs` (default `10`). |
| `notes` | string | no | Free text for the next agent. |

## `sources[]`

| Key | Type | Default | Meaning |
|---|---|---|---|
| `id` | string | — | Table name. Letters, digits, underscore. |
| `title` | string | `id` | What the business calls this file. |
| `match` | string or array | — | File name patterns, e.g. `["sales_*.xlsx"]`. |
| `format` | string | `xlsx` | `xlsx` or `csv`. |
| `sheet` | string, integer or null | first tab | Tab name or index. |
| `header_row` | integer | `1` | The Excel row holding the headings. |
| `delimiter` | string or null | detect | CSV only. |
| `required` | boolean | `true` | `false` lets a run proceed without this file. |
| `grain` | string | `""` | One sentence: what a row represents. |
| `business_key` | array | `[]` | Fields that identify the same record across files. Empty means identical rows are de-duplicated by their content. |
| `corrections_allowed` | boolean | `true` | May a later file change an existing record? `false` keeps the trusted value and lists the attempt. |
| `missing_record_policy` | string | `keep` | `keep` (absence means nothing) or `close` (absence means the record is finished - only correct when every file is a complete snapshot). |
| `columns` | array | — | The mapping; see below. |
| `filters` | array | `[]` | Rows deliberately out of scope. |
| `checks` | array | `[]` | Quality rules. |
| `control_totals` | array | `[]` | `{"field": "...", "precision": 2, "tolerance": "0"}`. |
| `notes` | string | `""` | Free text. |

## `sources[].columns[]`

| Key | Type | Default | Meaning |
|---|---|---|---|
| `source` | string | — | The heading exactly as it appears in Excel (matched case-insensitively, trimmed). |
| `field` | string | — | Internal name, used in SQL. |
| `type` | string | `text` | `text`, `number`, `integer`, `date`, `datetime`, `boolean`. |
| `required` | boolean | `false` | An empty value sends the row to quarantine. |
| `trim` | boolean | `true` | Remove surrounding spaces. |
| `default` | any | `null` | Used when the cell is empty. |
| `date_formats` | array | `[]` | Extra `strptime` patterns tried first, e.g. `["%d/%m/%Y"]`. |
| `notes` | string | `""` | Free text. |

Values the parser already understands without help: `1,234.50`, `1 234`,
`(50)` as negative, trailing-minus `12-`, Arabic decimal `12٫5`, the usual date
orders, `Yes`/`No`/`نعم`/`لا`, and an Excel serial number that lost its format.
A percentage such as `15%` is deliberately refused rather than guessed.

## What each layer creates in the database

| Object | Content |
|---|---|
| `stg__<id>` | Raw text exactly as read, with file name, hash and Excel row number |
| `clean__<id>` | Typed, checked rows for this run |
| `hist__<id>` | Trusted history: one row per business key, versioned |
| `v_<id>` | The active trusted records - **what your SQL reads** |
| `quarantine` | Rejected and warned rows, with the reason in plain language |
| `filtered_rows` | Rows excluded on purpose, so nothing is unaccounted for |
| `reconciliation` | Every proof, per run |
| `metrics`, `insights`, `runs`, `run_files`, `run_events` | Results and evidence per run |
