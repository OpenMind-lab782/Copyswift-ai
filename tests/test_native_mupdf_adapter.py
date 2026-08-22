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
