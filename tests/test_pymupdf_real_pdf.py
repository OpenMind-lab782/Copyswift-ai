import unittest

from ecosystem_core.document_adapters.pymupdf_adapter import PyMuPDFAdapter


class PyMuPDFRealPDFTests(unittest.TestCase):

    @staticmethod
    def _sample_pdf():
        try:
            import fitz
        except ImportError:
            return None

        document = fitz.open()

        page = document.new_page(
            width=595,
            height=842,
        )

        page.insert_text(
            (72, 100),
            "CopySwiftAI Document Studio",
        )

        payload = document.tobytes()
        document.close()

        return payload

    def test_real_pdf_parses_when_engine_available(self):
        payload = self._sample_pdf()

        if payload is None:
            self.skipTest(
                "PyMuPDF is unavailable in this runtime."
            )

        adapter = PyMuPDFAdapter()

        result = adapter.parse(
            payload,
            file_name="sample.pdf",
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(
            result["name"],
            "sample.pdf",
        )
        self.assertEqual(
            len(result["pages"]),
            1,
        )

        page = result["pages"][0]

        self.assertEqual(
            page["number"],
            1,
        )
        self.assertEqual(
            page["width"],
            595,
        )
        self.assertEqual(
            page["height"],
            842,
        )

    def test_real_pdf_reports_pdf_engine_metadata(self):
        payload = self._sample_pdf()

        if payload is None:
            self.skipTest(
                "PyMuPDF is unavailable in this runtime."
            )

        result = PyMuPDFAdapter().parse(
            payload,
            file_name="sample.pdf",
        )

        self.assertEqual(
            result["metadata"]["source_format"],
            "pdf",
        )
        self.assertEqual(
            result["metadata"]["parser_engine"],
            "pymupdf",
        )


if __name__ == "__main__":
    unittest.main()
