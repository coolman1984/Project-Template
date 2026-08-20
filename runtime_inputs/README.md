# Private runtime inputs

The final user must not install anything. The operator package therefore
carries its own Python runtime inside `Application/runtime/`.

Because this engine uses **only the Python standard library**, that runtime is
simply the official **Windows embeddable package** - no pip, no wheels, no
virtual environment, no compiler, no admin rights.

## One-time preparation

1. Download the Windows embeddable package for Python 3.11 or newer
   (`python-3.11.x-embed-amd64.zip`) from python.org on any machine with
   internet access.
2. Extract it into this folder as `runtime_inputs/python-windows/`, so that
   `runtime_inputs/python-windows/python.exe` exists.
3. Build the delivery:

   ```
   python PROJECT_TOOL.py deliver --project projects/<name> --output-dir release \
          --runtime runtime_inputs/python-windows
   ```

`package verify` **fails** if the runtime is missing, so a package that would
ask the user to install Python can never be delivered by accident.

## Why the embeddable build is enough

| Needed at run time | Where it comes from |
|---|---|
| Python interpreter | `runtime/python.exe`, `runtime/pythonw.exe` |
| Standard library | `runtime/python3xx.zip` (part of the embeddable build) |
| Database | `sqlite3`, part of the standard library |
| Web server | `http.server`, part of the standard library |
| Excel reading/writing | `engine/excel/*`, written against `zipfile` + `xml` |
| Page assets | `engine/webapp/static/*`, shipped in the package |

Nothing else is required, and nothing is downloaded when the user runs it.

## Note about this folder in Git

The runtime binaries are **not** committed - they are large and belong to
python.org. `.gitignore` keeps `runtime_inputs/python-windows/` out of the
repository. Only this README is tracked.
