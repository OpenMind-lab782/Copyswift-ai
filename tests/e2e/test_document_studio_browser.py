import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

FIXTURE_SHA256 = "1c43fe1a150bf3107e9d4cbe4b5b31f70c91e1728902c2e5486ecae337a8cad8"
FIXTURE_PDF_B64 = "JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNCAwIFIgPj4gL1hPYmplY3QgPDwgL0ltMSA1IDAgUiA+PiA+PiAvUGFyZW50IDIgMCBSIC9Db250ZW50cyA2IDAgUiA+PgplbmRvYmoKNCAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL1hPYmplY3QgL1N1YnR5cGUgL0ltYWdlIC9XaWR0aCAxIC9IZWlnaHQgMSAvQ29sb3JTcGFjZSAvRGV2aWNlUkdCIC9CaXRzUGVyQ29tcG9uZW50IDggL0xlbmd0aCAzID4+CnN0cmVhbQrIyMgKZW5kc3RyZWFtCmVuZG9iago2IDAgb2JqCjw8IC9MZW5ndGggMTM4ID4+CnN0cmVhbQpCVCAvRjEgMjAgVGYgNzIgNjkyIFRkIChCcm93c2VyIEUyRSBGaXh0dXJlKSBUaiBFVApCVCAvRjEgMTIgVGYgNzIgNjUyIFRkIChVbnJlbGF0ZWQgcHJlc2VydmVkIHRleHQpIFRqIEVUCnEgNDAgMCAwIDQwIDcyIDU3MiBjbSAvSW0xIERvIFEKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNwowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMTUgMDAwMDAgbiAKMDAwMDAwMDA2NCAwMDAwMCBuIAowMDAwMDAwMTIxIDAwMDAwIG4gCjAwMDAwMDAyNzMgMDAwMDAgbiAKMDAwMDAwMDM0MyAwMDAwMCBuIAowMDAwMDAwNDg4IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNyAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNjc3CiUlRU9GCg=="
PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADElEQVR4nGNgwA8AAQUBAScYxZcAAAAASUVORK5CYII="
REPO_ROOT = Path(__file__).resolve().parents[2]


def snapshot(element):
    return json.loads(json.dumps(element, sort_keys=True))


class DocumentStudioBrowserE2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="document-studio-browser-e2e-"))
        cls.artifacts = Path(os.environ.get("E2E_ARTIFACT_DIR", cls.tmp / "artifacts"))
        cls.artifacts.mkdir(parents=True, exist_ok=True)
        cls.fixture = cls.tmp / "fixture.pdf"
        fixture_bytes = base64.b64decode(FIXTURE_PDF_B64)
        cls.fixture.write_bytes(fixture_bytes)
        if hashlib.sha256(fixture_bytes).hexdigest() != FIXTURE_SHA256:
            raise AssertionError("deterministic PDF fixture SHA-256 mismatch")
        cls.image = cls.tmp / "replacement.png"
        cls.image.write_bytes(base64.b64decode(PNG_B64))
        cls.server_log = cls.artifacts / "server.log"
        env = os.environ.copy()
        env.update({
            "SWIFT_DB_BACKEND": "sqlite",
            "SWIFT_DATABASE": str(cls.tmp / "swift_payment.db"),
            "DATABASE_URL": f"sqlite:///{cls.tmp / 'document_studio.db'}",
            "SECRET_KEY": "document-studio-e2e-secret",
            "ADMIN_PASSWORD": "document-studio-e2e-admin",
            "PAYSTACK_ENGINE_MODE": "mock",
            "SWIFT_GATEWAY_MODE": "mock",
            "SWIFT_ENV": "development",
            "PYTHONPATH": str(REPO_ROOT),
        })
        cls.server = cls._start_server(env)
        import sqlite3
        with sqlite3.connect(cls.tmp / "copyswift.db") as db:
            db.execute("INSERT OR REPLACE INTO credits (email, balance) VALUES (?, ?)", ("document-studio-e2e@example.test", 60))
            db.commit()

    @classmethod
    def _start_server(cls, env):
        port = 18080
        log = cls.server_log.open("wb")
        proc = subprocess.Popen(
            [
                sys.executable, "-m", "flask", "--app", str(REPO_ROOT / "app.py"),
                "run", "--host", "127.0.0.1", "--port", str(port),
            ],
            cwd=cls.tmp,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        cls.base_url = f"http://127.0.0.1:{port}"
        deadline = time.time() + 30
        while time.time() < deadline:
            if proc.poll() is not None:
                log.close()
                raise RuntimeError("Flask E2E server exited during startup")
            try:
                with urlopen(cls.base_url + "/document-studio", timeout=2) as response:
                    if response.status == 200:
                        return proc
            except Exception:
                time.sleep(0.25)
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()
        raise RuntimeError("Flask E2E server did not become ready")

    @classmethod
    def tearDownClass(cls):
        proc = getattr(cls, "server", None)
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        if hasattr(cls, "tmp"):
            shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_full_browser_workflow(self):
        console_lines = []
        failed = False
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            page = context.new_page()
            page.on("console", lambda msg: console_lines.append(f"{msg.type}: {msg.text}"))
            try:
                page.goto(self.base_url + "/document-studio", wait_until="domcontentloaded")
                with page.expect_response(lambda r: r.url.endswith("/document-studio/identity") and r.request.method == "POST"):
                    page.locator("#email").fill("document-studio-e2e@example.test")
                    page.locator("#identityBtn").click()

                page.locator("#file").set_input_files(str(self.fixture))
                with page.expect_response(lambda r: r.url.endswith("/document-studio/import") and r.request.method == "POST") as import_response:
                    page.locator("#importBtn").click()
                response = import_response.value
                imported = response.json()
                self.assertEqual(response.status, 200)
                self.assertEqual(imported["original_sha256"], FIXTURE_SHA256)
                imported_doc = imported
                imported_page = imported_doc["pages"][0]
                self.assertEqual(imported_page["width"], 612)
                self.assertEqual(imported_page["height"], 792)
                imported_elements = imported_page["elements"]
                self.assertTrue(any(e.get("type") == "text" for e in imported_elements))
                self.assertTrue(any(e.get("type") == "image" for e in imported_elements))
                unrelated = next(e for e in imported_elements if e.get("content") == "Unrelated preserved text")
                original_text = next(e for e in imported_elements if e.get("content") == "Browser E2E Fixture")
                original_image = next(e for e in imported_elements if e.get("type") == "image")
                unrelated_before = snapshot(unrelated)
                original_text_before = snapshot(original_text)
                original_image_before = snapshot(original_image)
                token = imported["document_token"]
                revision = imported["revision"]

                text_locator = page.locator(f'.ds-element[data-element-id="{original_text["id"]}"]')
                text_locator.click()
                before_box = text_locator.bounding_box()
                self.assertIsNotNone(before_box)
                page.mouse.move(before_box["x"] + before_box["width"] / 2, before_box["y"] + before_box["height"] / 2)
                page.mouse.down()
                page.mouse.move(before_box["x"] + before_box["width"] / 2 + 30, before_box["y"] + before_box["height"] / 2 + 20)
                page.mouse.up()

                resize = text_locator.locator(".ds-resize-handle")
                resize_box = resize.bounding_box()
                self.assertIsNotNone(resize_box)
                page.mouse.move(resize_box["x"] + resize_box["width"] / 2, resize_box["y"] + resize_box["height"] / 2)
                page.mouse.down()
                page.mouse.move(resize_box["x"] + resize_box["width"] / 2 + 20, resize_box["y"] + resize_box["height"] / 2 + 10)
                page.mouse.up()

                page.locator("#ds-inspector textarea").fill("Browser E2E Fixture edited")
                page.locator('#ds-inspector input[placeholder="sans-serif"]').fill("serif")
                self.assertGreaterEqual(page.locator("#ds-inspector input[type=number]").count(), 1)
                page.locator("#ds-inspector input[type=number]").last.fill("22")
                page.locator('#ds-inspector input[placeholder="#111111"]').fill("#224466")

                page.locator(f'.ds-element[data-element-id="{original_image["id"]}"]').click()
                page.locator('#ds-inspector input[type="file"][accept="image/*"]').set_input_files(str(self.image))

                count_before_add = page.locator(".ds-element[data-element-id]").count()
                page.locator("#ds-add-text").click()
                page.wait_for_function("n => document.querySelectorAll('.ds-element[data-element-id]').length >= n", count_before_add + 1)
                page.locator(".ds-element[data-element-id]").last.click()
                page.locator("#ds-inspector textarea").fill("Added browser text")

                with page.expect_file_chooser() as chooser_info:
                    page.locator("#ds-add-image").click()
                chooser_info.value.set_files(str(self.image))
                page.wait_for_function("n => document.querySelectorAll('.ds-element[data-element-id]').length >= n", count_before_add + 2)

                page.locator("#ds-duplicate").click()
                page.wait_for_function("n => document.querySelectorAll('.ds-element[data-element-id]').length === n", count_before_add + 3)
                page.locator("#ds-delete").click()
                page.wait_for_function("n => document.querySelectorAll('.ds-element[data-element-id]').length === n", count_before_add + 2)

                self.assertEqual(page.locator("#ds-dirty").inner_text(), "Unsaved changes")
                with page.expect_response(lambda r: r.url.endswith("/document-studio/save") and r.request.method == "POST") as save_response:
                    page.locator("#ds-save").click()
                saved_response = save_response.value
                saved = saved_response.json()
                self.assertEqual(saved_response.status, 200)
                self.assertGreater(saved["revision"], revision)
                revision = saved["revision"]
                saved_doc = saved["document"]
                self.assertEqual(page.locator("#ds-dirty").inner_text(), "Saved")
                saved_elements = saved_doc["pages"][0]["elements"]
                saved_by_id = {e["id"]: e for e in saved_elements}
                self.assertNotEqual(saved_by_id[original_text["id"]]["x"], original_text_before["x"])
                self.assertNotEqual(saved_by_id[original_text["id"]]["width"], original_text_before["width"])
                self.assertEqual(saved_by_id[unrelated["id"]], unrelated_before)
                self.assertEqual(saved_by_id[original_image["id"]]["type"], "image")
                self.assertNotEqual(saved_by_id[original_image["id"]].get("image_data_base64"), original_image_before.get("image_data_base64"))

                stale_revision = max(0, revision - 1)
                conflict = page.evaluate(
                    """async ({token, revision, document}) => {
                        const response = await fetch('/document-studio/save', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({document_token: token, expected_revision: revision, document})
                        });
                        return {status: response.status, body: await response.json()};
                    }""",
                    {"token": token, "revision": stale_revision, "document": saved_doc},
                )
                self.assertEqual(conflict["status"], 409)
                self.assertEqual(page.locator("#ds-dirty").inner_text(), "Saved")

                with page.expect_download() as download_info:
                    page.locator("#exportBtn").click()
                download = download_info.value
                exported_path = self.artifacts / "exported.pdf"
                download.save_as(str(exported_path))
                self.assertGreater(exported_path.stat().st_size, 0)
                import fitz
                exported_pdf = fitz.open(exported_path)
                self.assertEqual(exported_pdf.page_count, 1)
                exported_text = exported_pdf[0].get_text()
                self.assertIn("Browser E2E Fixture edited", exported_text)
                self.assertIn("Unrelated preserved text", exported_text)
                exported_pdf.close()

                with page.expect_response(lambda r: r.url.endswith("/document-studio/reopen") and r.request.method == "POST") as reopen_response:
                    page.locator("#reopenBtn").click()
                reopened_response = reopen_response.value
                reopened = reopened_response.json()
                self.assertEqual(reopened_response.status, 200)
                self.assertEqual(reopened["document_token"], token)
                self.assertEqual(reopened["revision"], revision)
                self.assertEqual(reopened["original_sha256"], FIXTURE_SHA256)
                reopened_page = reopened["document"]["pages"][0]
                self.assertEqual(reopened_page["width"], 612)
                self.assertEqual(reopened_page["height"], 792)
                reopened_by_id = {e["id"]: e for e in reopened_page["elements"]}
                self.assertEqual(reopened_by_id[unrelated["id"]], unrelated_before)
                self.assertEqual(reopened_by_id[original_text["id"]]["content"], "Browser E2E Fixture edited")
                self.assertEqual(reopened_by_id[original_image["id"]]["type"], "image")
                self.assertTrue(any(e.get("content") == "Added browser text" for e in reopened_page["elements"]))
                self.assertTrue(any(e.get("type") == "image" and e.get("id") != original_image["id"] for e in reopened_page["elements"]))
                self.assertEqual(page.locator("#ds-dirty").inner_text(), "Saved")
            except Exception:
                failed = True
                page.screenshot(path=str(self.artifacts / "failure.png"), full_page=True)
                raise
            finally:
                (self.artifacts / "console.log").write_text("\n".join(console_lines), encoding="utf-8")
                if failed:
                    try:
                        context.tracing.stop(path=str(self.artifacts / "trace.zip"))
                    except Exception:
                        pass
                else:
                    context.tracing.stop()
                context.close()
                browser.close()
