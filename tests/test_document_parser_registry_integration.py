import unittest

from ecosystem_core.document_adapters import DocumentAdapterRegistry
from ecosystem_core.document_parser import DocumentParser


class DocumentParserRegistryIntegrationTests(unittest.TestCase):

    def test_parser_accepts_shared_adapter_registry(self):
        registry = DocumentAdapterRegistry()
        parser = DocumentParser(
            adapter_registry=registry
        )

        self.assertIs(
            parser.adapter_registry,
            registry,
        )

    def test_parser_reads_adapter_from_shared_registry(self):
        registry = DocumentAdapterRegistry()

        class PDFAdapter:
            def parse(self, data, file_name):
                return {
                    "name": file_name,
                    "pages": [],
                }

        registry.register("pdf", PDFAdapter())

        parser = DocumentParser(
            adapter_registry=registry
        )

        result = parser.parse(
            b"fake-pdf",
            file_name="sample.pdf",
        )

        self.assertEqual(
            result["name"],
            "sample.pdf",
        )

    def test_parser_can_use_registry_without_direct_adapter_dict(self):
        registry = DocumentAdapterRegistry()

        parser = DocumentParser(
            adapter_registry=registry
        )

        self.assertEqual(
            parser.supported_formats(),
            ["pdf", "docx"],
        )


if __name__ == "__main__":
    unittest.main()
