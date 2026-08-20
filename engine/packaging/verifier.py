"""Verify the final operator package.

This is the gate that keeps the product simple. If the ZIP does not have the
approved shape, or the launcher would ask the user to install anything, the
package is rejected before it reaches a person.
"""

from __future__ import annotations

import dataclasses
import posixpath
import re
import zipfile

ALLOWED_ROOT = {"START.bat", "QUICK_START.html", "Application"}
FORBIDDEN_IN_START = [
    (r"\bpip\b", "installs packages"),
    (r"\bpython\s+-m\s+(pip|venv|ensurepip)\b", "installs packages"),
    (r"\bconda\b|\bchoco\b|\bwinget\b|\bmsiexec\b", "installs software"),
    (r"\bgit\b", "uses Git"),
    (r"\bcurl\b|\bwget\b|Invoke-WebRequest|Invoke-RestMethod|bitsadmin", "downloads at run time"),
    (r"\bnetsh\b|\bnetstat\b|urlacl", "changes firewall or URL reservations"),
    (r"\brunas\b|\bsc\s+create\b|\breg\s+add\b|schtasks", "needs administrator rights"),
    (r"\bpy\s+-3\b|C:\\\\Python|Program Files\\\\Python", "uses a system Python"),
    (r"\bnpm\b|\bnode\b|\byarn\b", "needs Node.js"),
]
FORBIDDEN_APP_TOP = {".git", ".github", "tests", "wheelhouse", "node_modules", ".ai", "docs",
                     ".venv", "venv", "build", "dist"}


@dataclasses.dataclass
class Finding:
    level: str          # BLOCK | WARNING | INFO
    code: str
    message: str


@dataclasses.dataclass
class VerifyResult:
    zip_path: str
    project_name: str
    findings: list[Finding]
    entries: int

    @property
    def ok(self) -> bool:
        return not any(f.level == "BLOCK" for f in self.findings)

    def report(self) -> str:
        lines = [f"package: {self.zip_path}", f"entries: {self.entries}"]
        for finding in self.findings:
            lines.append(f"  [{finding.level}] {finding.code}: {finding.message}")
        lines.append("RESULT: PASS" if self.ok else "RESULT: FAIL")
        return "\n".join(lines)


def _unsafe(name: str) -> bool:
    if name.startswith("/") or name.startswith("\\") or ":" in name.split("/")[0][1:2] + "":
        return True
    if re.match(r"^[A-Za-z]:", name):
        return True
    parts = name.replace("\\", "/").split("/")
    return any(part == ".." for part in parts)


def verify(zip_path: str, require_runtime: bool = True) -> VerifyResult:
    findings: list[Finding] = []
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        if not names:
            return VerifyResult(zip_path, "", [Finding("BLOCK", "E-PKG-001", "the ZIP is empty")], 0)

        for name in names:
            if _unsafe(name):
                findings.append(Finding("BLOCK", "E-PKG-001", f"unsafe path in the ZIP: {name}"))

        roots = {name.replace("\\", "/").split("/")[0] for name in names}
        if len(roots) != 1:
            findings.append(Finding("BLOCK", "E-PKG-001",
                                    f"the ZIP must contain exactly one folder, found {sorted(roots)}"))
            project_name = sorted(roots)[0]
        else:
            project_name = roots.pop()

        prefix = project_name + "/"
        second_level = set()
        app_top = set()
        for name in names:
            normalised = name.replace("\\", "/")
            if not normalised.startswith(prefix):
                continue
            remainder = normalised[len(prefix):]
            if not remainder:
                continue
            parts = remainder.split("/")
            second_level.add(parts[0])
            if parts[0] == "Application" and len(parts) > 1 and parts[1]:
                app_top.add(parts[1])

        unexpected = sorted(second_level - ALLOWED_ROOT)
        if unexpected:
            findings.append(Finding("BLOCK", "E-PKG-001",
                                    f"unexpected entry at the package root: {unexpected}. "
                                    f"Only {sorted(ALLOWED_ROOT)} may be visible."))
        for required in ("START.bat", "QUICK_START.html", "Application"):
            if required not in second_level:
                findings.append(Finding("BLOCK", "E-PKG-001", f"{required} is missing"))

        exposed = sorted(name for name in app_top if name.lower() in FORBIDDEN_APP_TOP)
        if exposed:
            findings.append(Finding("BLOCK", "E-PKG-001",
                                    f"developer folder(s) exposed inside Application: {exposed}"))

        launch = f"{prefix}Application/app/launch.py"
        if launch not in names:
            findings.append(Finding("BLOCK", "E-PKG-001",
                                    "the application entry point Application/app/launch.py is missing"))

        runtime_files = [n for n in names if n.startswith(f"{prefix}Application/runtime/")]
        has_interpreter = any(posixpath.basename(n).lower() in ("python.exe", "pythonw.exe")
                              for n in runtime_files)
        if not has_interpreter:
            level = "BLOCK" if require_runtime else "WARNING"
            findings.append(Finding(
                level, "E-PKG-001",
                "no private runtime found (Application/runtime/python.exe). The user would need "
                "to install Python."))

        start_name = f"{prefix}START.bat"
        if start_name in names:
            content = archive.read(start_name).decode("utf-8", "replace")
            for pattern, why in FORBIDDEN_IN_START:
                if re.search(pattern, content, re.IGNORECASE):
                    findings.append(Finding("BLOCK", "E-PKG-001",
                                            f"START.bat {why} (matched /{pattern}/)"))
            if "Application" not in content:
                findings.append(Finding("BLOCK", "E-PKG-001",
                                        "START.bat does not start the internal application"))

        if not any(n.startswith(f"{prefix}Application/app/project/") for n in names):
            findings.append(Finding("BLOCK", "E-PKG-001",
                                    "the project configuration is missing from the package"))

    return VerifyResult(zip_path=zip_path, project_name=project_name, findings=findings,
                        entries=len(names))
