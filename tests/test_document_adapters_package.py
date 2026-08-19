import unittest

from ecosystem_core.document_adapters import DocumentAdapterRegistry


class DocumentAdaptersPackageTests(unittest.TestCase):

    def test_registry_initializes(self):
        registry = DocumentAdapterRegistry()

        self.assertIsNotNone(registry)

    def test_registry_can_register_pdf_adapter(self):
        registry = DocumentAdapterRegistry()

        class PDFAdapter:
            def parse(self, data, file_name):
                return {
                    "name": file_name,
                    "pages": [],
                }

        registry.register("pdf", PDFAdapter())

        self.assertIsInstance(
            registry.get("pdf"),
            PDFAdapter,
        )

    def test_registry_rejects_unsupported_format(self):
        registry = DocumentAdapterRegistry()

        class Adapter:
            def parse(self, data, file_name):
                return {}

        with self.assertRaises(ValueError):
            registry.register("xyz", Adapter())

    def test_registry_lists_registered_formats(self):
        registry = DocumentAdapterRegistry()

        class PDFAdapter:
            def parse(self, data, file_name):
                return {}

        class DOCXAdapter:
            def parse(self, data, file_name):
                return {}

        registry.register("pdf", PDFAdapter())
        registry.register("docx", DOCXAdapter())

        self.assertEqual(
            registry.list_formats(),
            ["docx", "pdf"],
        )


if __name__ == "__main__":
    unittest.main()
