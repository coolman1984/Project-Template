"""Idempotent, transactional connected history.

Running the same file twice must not create a second copy of anything. Every
record is identified by its business key; a changed record becomes a new
version of the same record, never a duplicate.
"""

from __future__ import annotations

import dataclasses
import datetime as _dt

from engine.data.clean import clean_table
from engine.db import database

HISTORY_COLUMNS = [
    ("_bk", "TEXT"), ("_row_hash", "TEXT"), ("_first_run", "TEXT"), ("_last_run", "TEXT"),
    ("_version", "INTEGER"), ("_status", "TEXT"), ("_updated_at", "TEXT"),
    ("_file", "TEXT"), ("_row_no", "INTEGER"),
]


@dataclasses.dataclass
class HistoryResult:
    source_id: str
    inserted: int = 0
    corrected: int = 0
    unchanged: int = 0
    closed: int = 0
    corrections_blocked: int = 0

    @property
    def touched(self) -> int:
        return self.inserted + self.corrected + self.unchanged


def history_table(source_id: str) -> str:
    return f"hist__{source_id}"


def view_name(source_id: str) -> str:
    return f"v_{source_id}"


def ensure(connection, source) -> None:
    table = history_table(source.id)
    database.create_table(
        connection, table,
        HISTORY_COLUMNS + [(c.field, database.SQL_TYPE[c.type]) for c in source.columns],
        primary_key=["_bk"])
    fields = ", ".join(database.quote(c.field) for c in source.columns)
    connection.execute(f"DROP VIEW IF EXISTS {database.quote(view_name(source.id))}")
    connection.execute(
        f"CREATE VIEW {database.quote(view_name(source.id))} AS "
        f"SELECT {fields}, _bk AS record_key, _version AS record_version, "
        f"_status AS record_status, _first_run AS first_run, _last_run AS last_run "
        f"FROM {database.quote(table)} WHERE _status = 'active'")


def apply(connection, run_id: str, source, quarantine_writer=None) -> HistoryResult:
    """Merge this run's clean rows into trusted history.

    The caller owns the transaction: on any failure the whole run rolls back and
    the previously trusted history stays exactly as it was.
    """

    ensure(connection, source)
    table = history_table(source.id)
    result = HistoryResult(source_id=source.id)
    now = _dt.datetime.now().isoformat(timespec="seconds")
    fields = [c.field for c in source.columns]

    rows = connection.execute(f"SELECT * FROM {database.quote(clean_table(source.id))}").fetchall()
    for row in rows:
        key = row["_bk"] or row["_row_hash"]
        existing = connection.execute(
            f"SELECT _row_hash, _version, _status FROM {database.quote(table)} WHERE _bk = ?",
            (key,)).fetchone()
        values = [row[field] for field in fields]
        if existing is None:
            connection.execute(
                f"INSERT INTO {database.quote(table)} "
                f"(_bk, _row_hash, _first_run, _last_run, _version, _status, _updated_at, _file,"
                f" _row_no, {', '.join(database.quote(f) for f in fields)}) "
                f"VALUES ({', '.join('?' for _ in range(9 + len(fields)))})",
                [key, row["_row_hash"], run_id, run_id, 1, "active", now, row["_file"],
                 row["_row_no"]] + values)
            result.inserted += 1
        elif existing["_row_hash"] == row["_row_hash"] and existing["_status"] == "active":
            connection.execute(
                f"UPDATE {database.quote(table)} SET _last_run = ?, _updated_at = ? WHERE _bk = ?",
                (run_id, now, key))
            result.unchanged += 1
        elif not source.corrections_allowed:
            result.corrections_blocked += 1
            if quarantine_writer is not None:
                quarantine_writer(
                    source.id, row["_file"], row["_row_no"], "correction_not_allowed",
                    ", ".join(source.business_key) or "record",
                    "This record already exists with different values and corrections are not "
                    "allowed for this source.",
                    {field: row[field] for field in fields})
        else:
            assignments = ", ".join(f"{database.quote(f)} = ?" for f in fields)
            connection.execute(
                f"UPDATE {database.quote(table)} SET {assignments}, _row_hash = ?, _last_run = ?, "
                f"_version = _version + 1, _status = 'active', _updated_at = ?, _file = ?, "
                f"_row_no = ? WHERE _bk = ?",
                values + [row["_row_hash"], run_id, now, row["_file"], row["_row_no"], key])
            result.corrected += 1

    if source.missing_record_policy == "close":
        cursor = connection.execute(
            f"UPDATE {database.quote(table)} SET _status = 'closed', _updated_at = ? "
            f"WHERE _status = 'active' AND _last_run <> ?", (now, run_id))
        result.closed = cursor.rowcount or 0
    return result
