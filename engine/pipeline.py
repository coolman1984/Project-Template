"""The deterministic run.

Every run follows exactly one order. A failed run never replaces the last
approved dashboard and never leaves trusted history half-updated: the whole
run is one database transaction, and the dashboard is only published after the
numbers have been verified.
"""

from __future__ import annotations

import dataclasses
import datetime as _dt
import json
import os
import platform
import traceback
from typing import Callable

from engine import __version__, config as config_module
from engine.data import archive, clean, history, insights, metrics, reconcile, staging
from engine.db import database
from engine.errors import UserError, user_error
from engine.excel import discovery
from engine.logging_setup import logger
from engine.report import dashboard as dashboard_module

ProgressCallback = Callable[[str, int, str], None]

STEPS = [
    ("prepare", 4, "Getting ready"),
    ("discover", 10, "Looking for your files"),
    ("stage", 28, "Reading the files"),
    ("validate", 46, "Checking the data"),
    ("history", 62, "Updating the trusted history"),
    ("reconcile", 72, "Proving the totals"),
    ("metrics", 84, "Calculating the results"),
    ("insights", 90, "Preparing the highlights"),
    ("publish", 97, "Publishing the dashboard"),
    ("done", 100, "Finished"),
]


@dataclasses.dataclass
class RunResult:
    run_id: str
    status: str                     # PASS | WARNING | BLOCK
    message: str
    started_at: str
    finished_at: str
    rows_in: int = 0
    rows_clean: int = 0
    rows_rejected: int = 0
    rows_filtered: int = 0
    files: list[dict] = dataclasses.field(default_factory=list)
    reconciliation: list[dict] = dataclasses.field(default_factory=list)
    sources: list[dict] = dataclasses.field(default_factory=list)
    error: dict | None = None
    dashboard_published: bool = False

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def new_run_id(now: _dt.datetime | None = None) -> str:
    now = now or _dt.datetime.now()
    return now.strftime("run_%Y%m%d_%H%M%S_%f")[:-3]


def run(config: config_module.ProjectConfig, workspace, progress: ProgressCallback | None = None,
        run_id: str | None = None, require_approval: bool = True) -> RunResult:
    """Execute one complete run and return its result."""

    log = logger()
    run_id = run_id or new_run_id()
    started_at = _dt.datetime.now().isoformat(timespec="seconds")
    events: list[tuple[str, int, str]] = []

    def emit(step: str, percent: int, message: str) -> None:
        events.append((step, percent, message))
        log.info("[%s] %3d%% %s", run_id, percent, message)
        if progress is not None:
            progress(step, percent, message)

    result = RunResult(run_id=run_id, status="RUNNING", message="", started_at=started_at,
                       finished_at="")
    connection = database.connect(workspace.database)
    try:
        emit(*_step("prepare"))
        database.migrate(connection)
        if require_approval and not config.is_approved:
            pending = config_module.pending_approvals(config)
            raise user_error(
                "E-CFG-005",
                what_happened="The business meaning of this report has not been approved yet.",
                next_action="Ask the person who owns these numbers to confirm the meaning, then process again.",
                detail=f"pending: {pending}")

        connection.execute(
            "INSERT OR REPLACE INTO runs(run_id, started_at, status, message) VALUES (?,?,?,?)",
            (run_id, started_at, "RUNNING", ""))

        connection.execute("BEGIN IMMEDIATE")
        try:
            checks: list[reconcile.Check] = []
            source_summaries: list[dict] = []

            emit(*_step("discover"))
            discovered: dict[str, list] = {}
            for source in config.sources:
                files = discovery.collect(source.id, workspace.inbox, source.match,
                                          workspace.staging_dir(run_id), required=source.required)
                discovered[source.id] = files
                for item in files:
                    connection.execute(
                        "INSERT OR REPLACE INTO run_files(run_id, source_id, file_name, size_bytes,"
                        " modified_at, sha256) VALUES (?,?,?,?,?,?)",
                        (run_id, source.id, item.file_name, item.size_bytes,
                         _dt.datetime.fromtimestamp(item.modified_at).isoformat(timespec="seconds"),
                         item.sha256))
                    result.files.append({"source_id": source.id, "file_name": item.file_name,
                                         "sha256": item.sha256, "size_bytes": item.size_bytes})

            emit(*_step("stage"))
            for source in config.sources:
                staged = staging.stage(connection, run_id, source, discovered[source.id])
                result.rows_in += staged.rows_read

            emit(*_step("validate"))
            cleaned: dict[str, clean.CleanResult] = {}
            for source in config.sources:
                outcome = clean.clean(connection, run_id, source)
                cleaned[source.id] = outcome
                result.rows_clean += outcome.rows_clean
                result.rows_rejected += outcome.rows_rejected
                result.rows_filtered += outcome.rows_filtered

            emit(*_step("history"))
            history_results: dict[str, history.HistoryResult] = {}

            def quarantine_writer(source_id, file_name, row_no, rule, field, message, payload):
                connection.execute(
                    "INSERT INTO quarantine(run_id, source_id, file_name, excel_row, rule, field,"
                    " message, severity, row_json) VALUES (?,?,?,?,?,?,?,?,?)",
                    (run_id, source_id, file_name, row_no, rule, field, message, "reject",
                     json.dumps(payload, ensure_ascii=False, default=str)))

            for source in config.sources:
                history_results[source.id] = history.apply(connection, run_id, source,
                                                           quarantine_writer)

            emit(*_step("reconcile"))
            for source in config.sources:
                checks.extend(reconcile.run(connection, run_id, source, history_results[source.id]))
            checks.extend(reconcile.relationships(connection, config, run_id))
            reconcile.save(connection, run_id, checks)
            result.reconciliation = reconcile.as_dicts(checks)

            for source in config.sources:
                outcome = cleaned[source.id]
                merged = history_results[source.id]
                source_summaries.append({
                    "source_id": source.id,
                    "title": source.title,
                    "grain": source.grain,
                    "files": [f.file_name for f in discovered[source.id]],
                    "rows_in": outcome.rows_in,
                    "rows_clean": outcome.rows_clean,
                    "rows_rejected": outcome.rows_rejected + merged.corrections_blocked,
                    "rows_filtered": outcome.rows_filtered,
                    "new_records": merged.inserted,
                    "corrected_records": merged.corrected,
                    "unchanged_records": merged.unchanged,
                    "closed_records": merged.closed,
                })
            result.sources = source_summaries

            status = reconcile.summary(checks)
            if status == "BLOCK" and config.gate("block_on_reconciliation_failure", True):
                raise user_error(
                    "E-REC-001",
                    what_happened="The totals from your files did not match the calculated totals.",
                    next_action=("Nothing was published. Check the highlighted files, then process "
                                 "again."),
                    trusted_data_safe=True,
                    detail=json.dumps(reconcile.as_dicts([c for c in checks if c.status == "BLOCK"]),
                                      ensure_ascii=False))

            max_rejected_pct = float(config.gate("max_rejected_percent", 100))
            if result.rows_in and (result.rows_rejected / result.rows_in) * 100 > max_rejected_pct:
                raise user_error(
                    "E-VAL-001",
                    what_happened=("Too many rows did not pass the agreed rules, so the result was "
                                   "not published."),
                    next_action="Review the listed rows in the source file and process again.",
                    detail=f"rejected={result.rows_rejected} of {result.rows_in}, "
                           f"limit={max_rejected_pct}%")

            emit(*_step("metrics"))
            definitions = metrics.parse_file(config.metrics_sql_path)
            payloads = metrics.compute(connection, definitions)
            metrics.save(connection, run_id, payloads)

            emit(*_step("insights"))
            highlights = insights.evaluate(config, payloads, {
                "rows_rejected": result.rows_rejected,
                "reconciliation": result.reconciliation,
            })
            insights.save(connection, run_id, highlights)

            emit(*_step("publish"))
            result.status = status
            result.message = _message_for(status, result)
            finished_at = _dt.datetime.now().isoformat(timespec="seconds")
            result.finished_at = finished_at

            document = dashboard_module.build(config, result, payloads, highlights, checks,
                                              connection, run_id, status)
            dashboard_module.verify(document, payloads)

            connection.execute(
                "UPDATE runs SET finished_at = ?, status = ?, rows_in = ?, rows_clean = ?,"
                " rows_rejected = ?, message = ?, manifest_json = ? WHERE run_id = ?",
                (finished_at, status, result.rows_in, result.rows_clean, result.rows_rejected,
                 result.message, json.dumps(_manifest(config, result), ensure_ascii=False,
                                            default=str), run_id))
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise

        # Published only after the transaction succeeded.
        archive.atomic_write(workspace.dashboard, json.dumps(document, ensure_ascii=False,
                                                             indent=2, default=str))
        result.dashboard_published = True
        archive.snapshot(workspace.archive, run_id,
                         [workspace.dashboard, workspace.database],
                         keep=int(config.gate("archive_keep_runs", 10)))
        _write_events(connection, run_id, events)
        emit(*_step("done"))
        _write_events(connection, run_id, events[-1:], offset=len(events) - 1)
        return result

    except UserError as exc:
        result.status = "BLOCK"
        result.error = exc.to_dict()
        result.message = exc.what_happened
        result.finished_at = _dt.datetime.now().isoformat(timespec="seconds")
        log.error("[%s] %s | %s", run_id, exc, exc.detail)
        _record_failure(connection, result)
        _write_events(connection, run_id, events + [("failed", 100, exc.what_happened)])
        return result
    except Exception as exc:  # unexpected - still never shown raw to the user
        detail = traceback.format_exc()
        log.error("[%s] unexpected failure\n%s", run_id, detail)
        wrapped = user_error(
            "E-RUN-001",
            what_happened="The run stopped before it finished. Your previous results were kept.",
            next_action="Try again. If it happens twice, send the support code to your support contact.",
            detail=detail)
        result.status = "BLOCK"
        result.error = wrapped.to_dict()
        result.message = wrapped.what_happened
        result.finished_at = _dt.datetime.now().isoformat(timespec="seconds")
        _record_failure(connection, result)
        _write_events(connection, run_id, events + [("failed", 100, wrapped.what_happened)])
        return result
    finally:
        connection.close()


def _step(name: str) -> tuple[str, int, str]:
    for step, percent, message in STEPS:
        if step == name:
            return step, percent, message
    return name, 0, name


def _message_for(status: str, result: RunResult) -> str:
    if status == "PASS":
        return f"{result.rows_clean:,} rows processed and every total matched."
    if status == "WARNING":
        return (f"{result.rows_clean:,} rows processed. Some rows need attention, "
                f"but the totals matched.")
    return "The result was not published."


def _manifest(config, result: RunResult) -> dict:
    return {
        "engine_version": __version__,
        "project": config.project_name,
        "run_id": result.run_id,
        "started_at": result.started_at,
        "status": result.status,
        "files": result.files,
        "rows": {"in": result.rows_in, "clean": result.rows_clean,
                 "rejected": result.rows_rejected, "filtered": result.rows_filtered},
        "reconciliation": result.reconciliation,
        "python": platform.python_version(),
        "platform": platform.platform(),
    }


def _record_failure(connection, result: RunResult) -> None:
    try:
        connection.execute(
            "INSERT OR REPLACE INTO runs(run_id, started_at, finished_at, status, rows_in,"
            " rows_clean, rows_rejected, message, manifest_json) VALUES (?,?,?,?,?,?,?,?,?)",
            (result.run_id, result.started_at, result.finished_at, "BLOCK", result.rows_in,
             result.rows_clean, result.rows_rejected, result.message,
             json.dumps({"error": result.error}, ensure_ascii=False)))
    except Exception:  # pragma: no cover - the database itself is unavailable
        logger().error("could not record the failed run %s", result.run_id)


def _write_events(connection, run_id: str, events, offset: int = 0) -> None:
    try:
        connection.executemany(
            "INSERT OR REPLACE INTO run_events(run_id, seq, at, step, percent, message)"
            " VALUES (?,?,?,?,?,?)",
            [(run_id, offset + index, _dt.datetime.now().isoformat(timespec="seconds"),
              step, percent, message) for index, (step, percent, message) in enumerate(events)])
    except Exception:  # pragma: no cover
        pass


def last_dashboard(workspace) -> dict | None:
    if not os.path.isfile(workspace.dashboard):
        return None
    try:
        with open(workspace.dashboard, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
