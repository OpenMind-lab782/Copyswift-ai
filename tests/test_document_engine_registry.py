import unittest

from ecosystem_core.document_parser import DocumentParser


class DocumentEngineRegistryTests(unittest.TestCase):

    def test_parser_accepts_multiple_engine_adapters(self):
        class PDFAdapter:
            def parse(self, data, file_name):
                return {"name": file_name, "pages": []}

        class DOCXAdapter:
            def parse(self, data, file_name):
                return {"name": file_name, "pages": []}

        parser = DocumentParser(
            adapters={
                "pdf": PDFAdapter(),
                "docx": DOCXAdapter(),
            }
        )

        self.assertIs(
            parser.adapters["pdf"].__class__,
            PDFAdapter,
        )
        self.assertIs(
            parser.adapters["docx"].__class__,
            DOCXAdapter,
        )

    def test_supported_format_without_adapter_remains_runtime_optional(self):
        class PDFAdapter:
            def parse(self, data, file_name):
                return {"name": file_name, "pages": []}

        parser = DocumentParser(
            adapters={"pdf": PDFAdapter()}
        )

        with self.assertRaises(RuntimeError):
            parser.parse(
                b"sample",
                file_name="document.docx",
            )

    def test_adapter_registry_can_be_replaced(self):
        parser = DocumentParser()

        class PDFAdapter:
            def parse(self, data, file_name):
                return {"name": file_name, "pages": []}

        parser.adapters["pdf"] = PDFAdapter()

        result = parser.parse(
            b"sample",
            file_name="document.pdf",
        )

        self.assertEqual(
            result["name"],
            "document.pdf",
        )


if __name__ == "__main__":
    unittest.main()
