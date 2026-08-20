"""Discover, fingerprint and safely copy approved input files.

Source files are never modified. Every run copies the inputs into its own
workspace and records a SHA-256 hash so lineage can be proven later.
"""

from __future__ import annotations

import dataclasses
import fnmatch
import hashlib
import os
import shutil

from engine.errors import user_error


@dataclasses.dataclass
class DiscoveredFile:
    source_id: str
    original_path: str
    workspace_path: str
    file_name: str
    size_bytes: int
    modified_at: float
    sha256: str


def hash_file(path: str, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_matching(inbox: str, patterns: list[str]) -> list[str]:
    if not os.path.isdir(inbox):
        return []
    found: list[str] = []
    for name in sorted(os.listdir(inbox)):
        if name.startswith("~$") or name.startswith("."):
            continue  # Excel lock files and hidden files are never inputs
        full = os.path.join(inbox, name)
        if not os.path.isfile(full):
            continue
        if any(fnmatch.fnmatch(name.lower(), pattern.lower()) for pattern in patterns):
            found.append(full)
    return found


def collect(source_id: str, inbox: str, patterns: list[str], workspace: str,
            required: bool = True) -> list[DiscoveredFile]:
    """Copy every matching file into ``workspace`` and fingerprint it."""

    matches = find_matching(inbox, patterns)
    if not matches and required:
        raise user_error(
            "E-IN-001",
            next_action=f"Add the file for '{source_id}' on the page, then press Process again.",
            detail=f"inbox={inbox} patterns={patterns}",
        )
    os.makedirs(workspace, exist_ok=True)
    collected: list[DiscoveredFile] = []
    for path in matches:
        before = os.stat(path)
        target = os.path.join(workspace, os.path.basename(path))
        shutil.copy2(path, target)
        after = os.stat(path)
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise user_error(
                "E-IN-004",
                next_action="Close the file in Excel and press Process again.",
                detail=f"{path} changed while being copied.",
            )
        collected.append(DiscoveredFile(
            source_id=source_id,
            original_path=path,
            workspace_path=target,
            file_name=os.path.basename(path),
            size_bytes=after.st_size,
            modified_at=after.st_mtime,
            sha256=hash_file(target),
        ))
    return collected
