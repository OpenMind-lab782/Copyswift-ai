import unittest

from ecosystem_core.document_renderer import DocumentRenderer
from ecosystem_core.kernel import EcosystemKernel


class DocumentRendererKernelIntegrationTests(unittest.TestCase):

    def test_kernel_exposes_document_renderer(self):
        kernel = EcosystemKernel()

        self.assertIsInstance(
            kernel.document_renderer,
            DocumentRenderer,
        )

    def test_document_studio_uses_kernel_renderer(self):
        kernel = EcosystemKernel()

        self.assertIs(
            kernel.document_studio.renderer,
            kernel.document_renderer,
        )

    def test_kernel_renderer_starts_with_lazy_pymupdf_engine(self):
        kernel = EcosystemKernel()

        self.assertIsNotNone(
            kernel.document_renderer.engine,
        )


if __name__ == "__main__":
    unittest.main()
