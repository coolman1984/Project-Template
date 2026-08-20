"""SQLite access and migrations.

One local analytical database per project. SQLite is part of the Python
standard library, so the packaged application carries no database server and
no driver install.
"""

from __future__ import annotations

import datetime as _dt
import os
import sqlite3
from typing import Iterable, Sequence

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")

SQL_TYPE = {
    "text": "TEXT",
    "number": "REAL",
    "integer": "INTEGER",
    "date": "TEXT",
    "datetime": "TEXT",
    "boolean": "INTEGER",
}


def connect(path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    connection = sqlite3.connect(path, isolation_level=None, timeout=30.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA synchronous=FULL")
    return connection


def migrate(connection: sqlite3.Connection) -> list[str]:
    """Apply every migration that has not run yet. Returns applied names."""

    connection.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "name TEXT PRIMARY KEY, applied_at TEXT NOT NULL)")
    done = {row["name"] for row in connection.execute("SELECT name FROM schema_migrations")}
    applied: list[str] = []
    for name in sorted(os.listdir(MIGRATIONS_DIR)):
        if not name.endswith(".sql") or name in done:
            continue
        with open(os.path.join(MIGRATIONS_DIR, name), "r", encoding="utf-8") as handle:
            connection.executescript(handle.read())
        connection.execute("INSERT INTO schema_migrations(name, applied_at) VALUES (?, ?)",
                           (name, _dt.datetime.now().isoformat(timespec="seconds")))
        applied.append(name)
    return applied


def quote(identifier: str) -> str:
    """Quote an identifier that the engine itself generated from config."""

    safe = "".join(ch for ch in identifier if ch.isalnum() or ch == "_")
    if safe != identifier or not safe:
        raise ValueError(f"unsafe identifier: {identifier!r}")
    return f'"{safe}"'


def create_table(connection: sqlite3.Connection, name: str,
                 columns: Sequence[tuple[str, str]], primary_key: Sequence[str] = ()) -> None:
    parts = [f"{quote(column)} {kind}" for column, kind in columns]
    if primary_key:
        parts.append("PRIMARY KEY (" + ", ".join(quote(c) for c in primary_key) + ")")
    connection.execute(f"CREATE TABLE IF NOT EXISTS {quote(name)} ({', '.join(parts)})")


def drop_table(connection: sqlite3.Connection, name: str) -> None:
    connection.execute(f"DROP TABLE IF EXISTS {quote(name)}")


def insert_many(connection: sqlite3.Connection, table: str, columns: Sequence[str],
                rows: Iterable[Sequence[object]]) -> int:
    placeholders = ", ".join("?" for _ in columns)
    column_list = ", ".join(quote(c) for c in columns)
    cursor = connection.executemany(
        f"INSERT INTO {quote(table)} ({column_list}) VALUES ({placeholders})", rows)
    return cursor.rowcount or 0


def table_exists(connection: sqlite3.Connection, name: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table','view') AND name = ?", (name,)).fetchone()
    return row is not None


def scalar(connection: sqlite3.Connection, sql: str, params: Sequence[object] = ()) -> object:
    row = connection.execute(sql, params).fetchone()
    return None if row is None else row[0]
