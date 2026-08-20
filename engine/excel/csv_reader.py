"""CSV / TSV reader with the same shape as the .xlsx reader."""

from __future__ import annotations

import csv
import io

from engine.errors import user_error


def read_block(path: str, delimiter: str | None = None, header_row: int = 1,
               max_rows: int | None = None) -> tuple[list[str], list[tuple[int, list[object]]]]:
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            text = handle.read()
    except OSError as exc:
        raise user_error("E-IN-002", "Re-save the file and add it again.",
                         detail=f"{path}: {exc}") from exc
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(text[:4096], delimiters=",;\t|").delimiter
        except csv.Error:
            delimiter = ","
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    headers: list[str] = []
    rows: list[tuple[int, list[object]]] = []
    for index, values in enumerate(reader, start=1):
        if index < header_row:
            continue
        if index == header_row:
            headers = [v.strip() for v in values]
            continue
        if not any(v.strip() for v in values):
            continue
        rows.append((index, list(values)))
        if max_rows is not None and len(rows) >= max_rows:
            break
    return headers, rows
