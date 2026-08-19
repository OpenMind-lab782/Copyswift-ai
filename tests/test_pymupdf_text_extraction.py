import unittest

from ecosystem_core.document_adapters.pymupdf_adapter import PyMuPDFAdapter


class PyMuPDFTextExtractionTests(unittest.TestCase):

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

    def test_text_element_is_extracted(self):
        payload = self._sample_pdf()

        if payload is None:
            self.skipTest(
                "PyMuPDF is unavailable in this runtime."
            )

        result = PyMuPDFAdapter().parse(
            payload,
            file_name="sample.pdf",
        )

        elements = result["pages"][0]["elements"]

        text_elements = [
            element
            for element in elements
            if element.get("type") == "text"
        ]

        self.assertGreaterEqual(
            len(text_elements),
            1,
        )

        self.assertIn(
            "CopySwiftAI Document Studio",
            text_elements[0]["content"],
        )

    def test_text_element_contains_position_and_size(self):
        payload = self._sample_pdf()

        if payload is None:
            self.skipTest(
                "PyMuPDF is unavailable in this runtime."
            )

        result = PyMuPDFAdapter().parse(
            payload,
            file_name="sample.pdf",
        )

        text_element = next(
            element
            for element in result["pages"][0]["elements"]
            if element.get("type") == "text"
        )

        for field in ("x", "y", "width", "height"):
            self.assertIn(
                field,
                text_element,
            )

    def test_text_element_has_stable_id(self):
        payload = self._sample_pdf()

        if payload is None:
            self.skipTest(
                "PyMuPDF is unavailable in this runtime."
            )

        result = PyMuPDFAdapter().parse(
            payload,
            file_name="sample.pdf",
        )

        text_element = next(
            element
            for element in result["pages"][0]["elements"]
            if element.get("type") == "text"
        )

        self.assertTrue(
            str(text_element.get("id", "")).strip()
        )


if __name__ == "__main__":
    unittest.main()
