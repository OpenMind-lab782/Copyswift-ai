import unittest
from pathlib import Path
import subprocess
from ecosystem_core.document_adapters.native_mupdf_adapter import NativeMuPDFAdapter

class NativeMuPDFAdapterTests(unittest.TestCase):
    def test_adapter_initializes_and_detects_mutool(self):
        adapter = NativeMuPDFAdapter()
        self.assertTrue(adapter.mutool)

    def test_adapter_exposes_parse_method(self):
        self.assertTrue(callable(NativeMuPDFAdapter().parse))

    def test_adapter_extracts_text_geometry_and_font_metadata(self):
        page_file = Path("native-mupdf-text-page.txt")
        pdf_file = Path("native-mupdf-text.pdf")
        try:
            page_file.write_text(
                "%%MediaBox 0 0 300 300\nBT\n/F1 18 Tf\n72 200 Td\n"
                "(Native MuPDF Test) Tj\nET\n"
            )
            subprocess.run(
                ["mutool", "create", "-o", str(pdf_file), str(page_file)],
                check=True,
                capture_output=True,
            )
            result = NativeMuPDFAdapter().parse(
                pdf_file.read_bytes(),
                "native-mupdf-text.pdf",
            )
            page = result["pages"][0]
            element = page["elements"][0]
            self.assertEqual(element["type"], "text")
            self.assertEqual(element["content"], "Native MuPDF Test")
            self.assertEqual(element["font_size"], 18.0)
            self.assertEqual(element["color"], "#000000")
            self.assertGreater(element["width"], 0)
            self.assertGreater(element["height"], 0)
        finally:
            page_file.unlink(missing_ok=True)
            pdf_file.unlink(missing_ok=True)

    def test_adapter_parses_real_pdf(self):
        page_file = Path("native-mupdf-test-page.txt")
        pdf_file = Path("native-mupdf-test.pdf")
        try:
            page_file.write_text("%%MediaBox 0 0 300 300\n")
            subprocess.run(["mutool", "create", "-o", str(pdf_file), str(page_file)], check=True, capture_output=True)
            result = NativeMuPDFAdapter().parse(pdf_file.read_bytes(), "native-mupdf-test.pdf")
            self.assertEqual(result["metadata"]["parser_engine"], "native-mupdf")
            self.assertEqual(len(result["pages"]), 1)
        finally:
            page_file.unlink(missing_ok=True)
            pdf_file.unlink(missing_ok=True)

if __name__ == "__main__":
    unittest.main()
