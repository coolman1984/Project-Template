"""Browser verification.

Optional: it runs only where a Chromium build and the Playwright package are
available. It is the proof that the page really renders the approved numbers,
asks the internet for nothing, and stays readable in both languages.

Skipping this test is not the same as passing it - a delivery still needs the
page opened once on the target machine.
"""

from __future__ import annotations

import base64
import glob
import json
import os
import threading
import time
import unittest
import urllib.request

from tests.helpers import FIXTURES, example_config, example_workspace, remove_all

from engine.webapp import server as server_module

try:  # pragma: no cover - environment dependent
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None


def chromium_path() -> str | None:
    root = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    for candidate in sorted(glob.glob(os.path.join(root, "chromium-*", "chrome-linux", "chrome"))):
        return candidate
    for candidate in sorted(glob.glob(os.path.join(root, "chromium-*", "chrome-win", "chrome.exe"))):
        return candidate
    return None


@unittest.skipUnless(sync_playwright is not None and chromium_path(),
                     "Playwright and a local Chromium build are required")
class BrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cleanup: list[str] = []
        cls.workspace = example_workspace(cls.cleanup, with_fixtures=False)
        cls.server, cls.application = server_module.make_server(example_config(), cls.workspace)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.url = server_module.url_for(cls.server, cls.application)
        cls.key = cls.application.session_key
        cls.base = cls.url.split("/?k=")[0]

        payload = []
        for name in ("sales_2026Q1.xlsx", "customers.xlsx"):
            with open(os.path.join(FIXTURES, name), "rb") as handle:
                payload.append({"name": name,
                                "content_base64": base64.b64encode(handle.read()).decode()})
        cls.call("/api/files", {"files": payload})
        cls.call("/api/process", {})
        for _ in range(240):
            progress = cls.call("/api/progress")
            if not progress["busy"]:
                break
            time.sleep(0.25)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        remove_all(cls.cleanup)

    @classmethod
    def call(cls, path: str, payload=None):
        separator = "&" if "?" in path else "?"
        request = urllib.request.Request(
            f"{cls.base}{path}{separator}k={cls.key}",
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode())

    def test_the_page_shows_the_approved_numbers_and_asks_the_internet_for_nothing(self) -> None:
        problems: list[str] = []
        external: list[str] = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=chromium_path(),
                                                 args=["--no-sandbox"])
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.on("pageerror", lambda error: problems.append(str(error)))
            page.on("console", lambda message: problems.append(message.text)
                    if message.type == "error" else None)
            page.on("request", lambda request: external.append(request.url)
                    if not request.url.startswith(("http://127.0.0.1", "data:")) else None)

            page.goto(self.url, wait_until="networkidle")
            page.wait_for_selector(".kpi .value")

            shown = page.eval_on_selector_all(
                ".kpi", "cards => cards.map(c => c.querySelector('.value').textContent)")
            self.assertIn("298,944.47 SAR", shown[0])
            self.assertEqual(page.inner_text("#status-pill"), "WARNING")
            self.assertEqual(page.eval_on_selector_all("svg.chart", "charts => charts.length"), 2)
            self.assertGreater(
                page.eval_on_selector_all("#attention-table tbody tr", "rows => rows.length"), 0)
            self.assertGreater(
                page.eval_on_selector_all("#reconciliation-table tbody tr", "rows => rows.length"), 0)

            # No sideways scrolling, in either language, at any width.
            for language in ("en", "ar"):
                if language == "ar":
                    page.click("#lang-toggle")
                    page.wait_for_timeout(300)
                    self.assertEqual(page.get_attribute("html", "dir"), "rtl")
                for width in (1280, 900, 420):
                    page.set_viewport_size({"width": width, "height": 900})
                    page.wait_for_timeout(150)
                    self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"),
                                         width, f"{language} @{width}px scrolls sideways")

            page.emulate_media(media="print")
            self.assertFalse(page.is_visible("#files-card"),
                             "the file box must not appear on a printed page")
            browser.close()

        self.assertEqual(problems, [], "the page reported errors")
        self.assertEqual(external, [], "the page asked the internet for something")


if __name__ == "__main__":
    unittest.main()
