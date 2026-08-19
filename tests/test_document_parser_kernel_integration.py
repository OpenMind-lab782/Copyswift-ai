import unittest

from ecosystem_core.document_parser import DocumentParser
from ecosystem_core.kernel import EcosystemKernel


class DocumentParserKernelIntegrationTests(unittest.TestCase):

    def test_kernel_exposes_document_parser(self):
        kernel = EcosystemKernel()

        self.assertIsNotNone(kernel.document_parser)

    def test_kernel_exposes_document_parser_service(self):
        kernel = EcosystemKernel()

        self.assertIsInstance(
            kernel.document_parser,
            DocumentParser,
        )

    def test_document_studio_uses_kernel_parser(self):
        kernel = EcosystemKernel()

        self.assertIs(
            kernel.document_studio.parser,
            kernel.document_parser,
        )

    def test_document_parser_shared_instance_is_stable(self):
        kernel = EcosystemKernel()

        self.assertIs(
            kernel.document_studio.parser,
            kernel.document_parser,
        )


if __name__ == "__main__":
    unittest.main()
