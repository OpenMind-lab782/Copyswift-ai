import unittest

from ecosystem_core.document_adapters.pymupdf_adapter import PyMuPDFAdapter
from ecosystem_core.kernel import EcosystemKernel


class PyMuPDFKernelIntegrationTests(unittest.TestCase):

    def test_kernel_can_register_pymupdf_adapter(self):
        kernel = EcosystemKernel()
        adapter = PyMuPDFAdapter()

        kernel.register_document_adapter(
            "pdf",
            adapter,
        )

        self.assertIs(
            kernel.document_parser.adapter_registry.get("pdf"),
            adapter,
        )

    def test_kernel_reports_pdf_adapter_as_registered(self):
        kernel = EcosystemKernel()

        kernel.register_document_adapter(
            "pdf",
            PyMuPDFAdapter(),
        )

        self.assertTrue(
            kernel.document_parser.adapter_registry.exists("pdf")
        )

    def test_document_studio_uses_kernel_parser_after_registration(self):
        kernel = EcosystemKernel()

        kernel.register_document_adapter(
            "pdf",
            PyMuPDFAdapter(),
        )

        self.assertIs(
            kernel.document_studio.parser,
            kernel.document_parser,
        )


if __name__ == "__main__":
    unittest.main()
