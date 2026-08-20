# Finishing the template on a Windows PC

One task, done once. After this, every report built from this template runs on
any Windows PC with nothing to install.

Everything below is a checklist. Do not change anything under `engine/`, and do
not add any Python package: the engine is standard-library only on purpose.

---

## Step 1 - add the private Windows runtime

The delivered package carries its own Python so the final user never installs
anything. Because the engine uses only the standard library, the official
**Windows embeddable package** is all that is needed - no pip, no wheels.

1. Download `python-3.11.9-embed-amd64.zip` (or any newer 3.11+/3.12+
   `embed-amd64` build) from <https://www.python.org/downloads/windows/>.
   It is roughly 10 MB.
2. Extract it into the repository so this exact path exists:

   ```
   runtime_inputs\python-windows\python.exe
   ```

   `pythonw.exe` and `python3xx.zip` must sit next to it. Do not create an extra
   folder level - if you see `runtime_inputs\python-windows\python-3.11.9-embed-amd64\python.exe`,
   move the files up one level.
3. Do not commit those files. `.gitignore` already excludes them; they belong to
   python.org, not to this repository.

Check it:

```bat
dir runtime_inputs\python-windows\python.exe
```

---

## Step 2 - run the test suite

```bat
python PROJECT_TOOL.py test
```

Expected: `OK`, with every test passing. `tests/test_browser.py` skips itself
unless Playwright and a local Chromium are installed - a skip is fine here, and
a skip is not a pass.

---

## Step 3 - build the example delivery

```bat
python PROJECT_TOOL.py deliver --project projects\example_sales --output-dir release --runtime runtime_inputs\python-windows
```

Expected: the last line is `RESULT: PASS`, and `release\ExampleSales.zip` exists
(roughly 15-25 MB, because it now contains the runtime).

If it says `no private runtime found`, Step 1 is not finished.

---

## Step 4 - be the final user

1. Copy `release\ExampleSales.zip` to the Desktop and extract it there.
2. Open the `ExampleSales` folder. It must contain exactly three things:
   `START.bat`, `QUICK_START.html`, `Application`.
3. Double-click **START.bat**.
   - If Windows shows *"Windows protected your PC"*, choose **More info →
     Run anyway**. That warning appears for any newly created `.bat` file; it is
     not a fault in the package.
4. The browser opens by itself.
5. Drag these two files onto the page:
   `projects\example_sales\fixtures\sales_2026Q1.xlsx` and
   `projects\example_sales\fixtures\customers.xlsx`
6. Press **Process**.

Expected result, exactly:

| What | Value |
|---|---|
| Status | `WARNING` |
| Total revenue | `298,944.47 SAR` |
| Invoices | `55` |
| Average invoice | `5,435.35 SAR` |
| Customers served | `12` |
| Rows read / used / needing attention / out of scope | `124 / 121 / 2 / 1` |
| Every reconciliation check | `PASS`, except `link_to_customers` which is `WARNING` |

Any other numbers mean something is wrong. Report it - do not adjust the
expected values to match.

---

## Step 5 - prove it is really offline

With the application still open: turn off Wi-Fi (or unplug the network), press
**Process** again, and confirm the run still completes.

Expected: the same totals, and the source summary shows `0` new records - the
second run recognises the same data instead of duplicating it.

---

## Step 6 - record what was proved

Edit `.ai/CURRENT_STATE.md` and move these rows out of the `CONDITIONAL` table
into the verified table, with the date and the Windows version used:

- double-click `START.bat` on a clean Windows machine;
- private Windows runtime included in the ZIP;
- browser behaviour on Edge/Chrome on Windows.

Leave the "non-technical operator completes two runs and one recovery" row in
`CONDITIONAL` until a real person has actually done it.

Then commit and push:

```bat
git add -A
git commit -m "Verify the offline package on Windows"
git push
```

---

## Step 7 - hand over the template

```bat
python tools\make_template_zip.py
```

This writes `release\Project-Template.zip`. That file - not this repository - is
what a business user attaches to a chat, together with their Excel files and a
plain explanation of the work.

---

## If a step fails

The application always shows a support code such as `E-IN-001`. Look it up in
`docs/TROUBLESHOOTING.md`, and read `Application\Data\logs\application.log`
inside the extracted package.

Fix the cause, not the symptom. In particular:

- never edit `tests/` or `projects/example_sales/tests/golden.json` to make a
  failure disappear;
- never remove a check from `engine/packaging/verifier.py`;
- never ask the final user to install anything.
