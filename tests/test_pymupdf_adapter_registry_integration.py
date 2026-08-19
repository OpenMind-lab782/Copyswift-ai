import unittest

from ecosystem_core.document_adapters import DocumentAdapterRegistry
from ecosystem_core.document_adapters.pymupdf_adapter import PyMuPDFAdapter


class PyMuPDFAdapterRegistryIntegrationTests(unittest.TestCase):

    def test_pymupdf_adapter_registers_as_pdf_adapter(self):
        registry = DocumentAdapterRegistry()
        adapter = PyMuPDFAdapter()

        registry.register("pdf", adapter)

        self.assertIs(
            registry.get("pdf"),
            adapter,
        )

    def test_pymupdf_adapter_appears_in_registered_formats(self):
        registry = DocumentAdapterRegistry()

        registry.register(
            "pdf",
            PyMuPDFAdapter(),
        )

        self.assertEqual(
            registry.list_formats(),
            ["pdf"],
        )

    def test_pymupdf_adapter_satisfies_registry_contract(self):
        registry = DocumentAdapterRegistry()

        adapter = PyMuPDFAdapter()
        registry.register("pdf", adapter)

        self.assertTrue(
            registry.exists("pdf")
        )
        self.assertTrue(
            callable(adapter.parse)
        )


if __name__ == "__main__":
    unittest.main()
