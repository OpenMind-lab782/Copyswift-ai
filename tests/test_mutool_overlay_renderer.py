import base64
import unittest

from ecosystem_core.document_adapters.native_mupdf_adapter import NativeMuPDFAdapter
from ecosystem_core.document_renderers.mutool_overlay_renderer import MutoolOverlayRenderer


class MutoolOverlayRendererTests(unittest.TestCase):
    def _pdf(self):
        import subprocess
        from pathlib import Path
        src = Path("native-renderer-fixture.txt")
        pdf = Path("native-renderer-fixture.pdf")
        try:
            src.write_text("%%MediaBox 0 0 300 300\nBT\n/F1 18 Tf\n72 200 Td\n(Original) Tj\nET\n")
            subprocess.run(["mutool", "create", "-o", str(pdf), str(src)], check=True, capture_output=True)
            return pdf.read_bytes()
        finally:
            src.unlink(missing_ok=True)
            pdf.unlink(missing_ok=True)

    def _document(self, *, content="Original", font="Helvetica", font_size=18, color="#000000", image_data=None):
        image = {
            "id": "image-1",
            "type": "image",
            "x": 120,
            "y": 180,
            "width": 80,
            "height": 60,
            "image_format": "png",
        }
        if image_data is not None:
            image["image_data"] = image_data
        return {
            "name": "native-renderer.pdf",
            "pages": [{
                "number": 1,
                "width": 300,
                "height": 300,
                "elements": [{
                    "id": "text-1",
                    "type": "text",
                    "content": content,
                    "x": 72,
                    "y": 90,
                    "width": 100,
                    "height": 22,
                    "font": font,
                    "font_size": font_size,
                    "color": color,
                }, image],
            }],
        }

    def _prepare(self, document):
        import hashlib
        import copy
        source = self._pdf()
        document = copy.deepcopy(document)
        document["original_pages"] = copy.deepcopy(document["pages"])
        document["original_bytes"] = source
        document["original_sha256"] = hashlib.sha256(source).hexdigest()
        return document

    def test_text_content_change_produces_native_render(self):
        document = self._prepare(self._document(content="Updated"))
        document["original_pages"][0]["elements"][0]["content"] = "Original"
        rendered = MutoolOverlayRenderer().render(document, "text.pdf")
        parsed = NativeMuPDFAdapter().parse(rendered, "text.pdf")
        contents = [e.get("content") for e in parsed["pages"][0]["elements"] if e.get("type") == "text"]
        self.assertIn("Updated", contents)

    def test_style_only_change_produces_native_render_operation(self):
        baseline = self._document(font="Helvetica-Bold", font_size=16, color="#000000")
        document = self._prepare(self._document(font="Helvetica", font_size=20, color="#FF0000"))
        document["original_pages"] = baseline["pages"]
        ops = MutoolOverlayRenderer._build_ops(document["pages"], document["original_pages"])
        self.assertEqual(len(ops["pages"][0]["text_inserts"]), 1)
        self.assertEqual(ops["pages"][0]["text_inserts"][0]["font_size"], 20)

    def test_image_edit_uses_document_image_data(self):
        baseline = self._document(image_data=b"OLD")
        document = self._prepare(self._document(image_data=b"NEW"))
        document["original_pages"] = baseline["pages"]
        ops = MutoolOverlayRenderer._build_ops(document["pages"], document["original_pages"])
        image_inserts = ops["pages"][0]["image_inserts"]
        self.assertEqual(len(image_inserts), 1)
        self.assertTrue(image_inserts[0]["png_base64"])
        self.assertEqual(base64.b64decode(image_inserts[0]["png_base64"]), b"NEW")


if __name__ == "__main__":
    unittest.main()
