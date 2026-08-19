import unittest

from ecosystem_core.document_parser import DocumentParser
from ecosystem_core.kernel import EcosystemKernel


class DocumentEngineRegistryKernelTests(unittest.TestCase):

    def test_kernel_exposes_document_parser_registry(self):
        kernel = EcosystemKernel()

        self.assertIsInstance(
            kernel.document_parser,
            DocumentParser,
        )

    def test_document_studio_uses_kernel_document_parser(self):
        kernel = EcosystemKernel()

        self.assertIs(
            kernel.document_studio.parser,
            kernel.document_parser,
        )

    def test_kernel_parser_registry_starts_without_optional_engines(self):
        kernel = EcosystemKernel()

        self.assertEqual(
            kernel.document_parser.adapters,
            {},
        )


if __name__ == "__main__":
    unittest.main()
