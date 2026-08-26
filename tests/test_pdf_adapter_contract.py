import unittest

from ecosystem_core.document_parser import DocumentParser


class ProductionPDFAdapterContractTests(unittest.TestCase):

    def test_pdf_adapter_must_expose_parse_method(self):
        class PDFAdapter:
            def parse(self, data, file_name):
                return {
                    "name": file_name,
                    "pages": [],
                }

        parser = DocumentParser(
            adapters={"pdf": PDFAdapter()}
        )

        result = parser.parse(
            b"fake-pdf",
            file_name="document.pdf",
        )

        self.assertEqual(result["name"], "document.pdf")
        self.assertIn("pages", result)

    def test_pdf_adapter_output_must_be_document_like(self):
        class PDFAdapter:
            def parse(self, data, file_name):
                return {
                    "name": file_name,
                    "pages": [
                        {
                            "number": 1,
                            "width": 595,
                            "height": 842,
                            "elements": [],
                        }
                    ],
                }

        parser = DocumentParser(
            adapters={"pdf": PDFAdapter()}
        )

        result = parser.parse(
            b"fake-pdf",
            file_name="document.pdf",
        )

        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["pages"], list)

    def test_pdf_adapter_preserves_filename(self):
        captured = {}

        class PDFAdapter:
            def parse(self, data, file_name):
                captured["file_name"] = file_name
                return {"name": file_name, "pages": []}

        parser = DocumentParser(
            adapters={"pdf": PDFAdapter()}
        )

        parser.parse(
            b"fake-pdf",
            file_name="original-document.pdf",
        )

        self.assertEqual(
            captured["file_name"],
            "original-document.pdf",
        )


if __name__ == "__main__":
    unittest.main()
