import unittest

from ecosystem_core.document_parser import DocumentParser


class PDFAdapterRuntimeBoundaryTests(unittest.TestCase):

    def test_pdf_adapter_can_be_unavailable_without_breaking_parser(self):
        parser = DocumentParser(
            adapters={}
        )

        with self.assertRaises(RuntimeError):
            parser.parse(
                b"sample-pdf",
                file_name="sample.pdf",
            )

    def test_pdf_adapter_failure_isolated_from_parser_contract(self):
        class FailingPDFAdapter:
            def parse(self, data, file_name):
                raise RuntimeError("PDF engine unavailable.")

        parser = DocumentParser(
            adapters={"pdf": FailingPDFAdapter()}
        )

        with self.assertRaises(RuntimeError):
            parser.parse(
                b"sample-pdf",
                file_name="sample.pdf",
            )

    def test_docx_adapter_can_remain_independent(self):
        class FakeDOCXAdapter:
            def parse(self, data, file_name):
                return {
                    "name": file_name,
                    "pages": [],
                }

        parser = DocumentParser(
            adapters={"docx": FakeDOCXAdapter()}
        )

        result = parser.parse(
            b"sample-docx",
            file_name="sample.docx",
        )

        self.assertEqual(result["name"], "sample.docx")


if __name__ == "__main__":
    unittest.main()
