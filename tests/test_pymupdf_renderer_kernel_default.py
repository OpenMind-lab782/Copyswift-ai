import unittest

from ecosystem_core.document_renderers.pymupdf_renderer import PyMuPDFRenderer
from ecosystem_core.kernel import EcosystemKernel


class PyMuPDFRendererKernelDefaultTests(unittest.TestCase):

    def test_kernel_exposes_pymupdf_renderer_engine(self):
        kernel = EcosystemKernel()

        self.assertIsInstance(
            kernel.document_renderer.engine,
            PyMuPDFRenderer,
        )

    def test_document_studio_uses_kernel_pymupdf_renderer(self):
        kernel = EcosystemKernel()

        self.assertIs(
            kernel.document_studio.renderer.engine,
            kernel.document_renderer.engine,
        )

    def test_pymupdf_engine_remains_lazy_in_termux(self):
        kernel = EcosystemKernel()

        engine = kernel.document_renderer.engine

        self.assertIsInstance(
            engine,
            PyMuPDFRenderer,
        )
        self.assertTrue(
            hasattr(engine, "_engine")
        )


if __name__ == "__main__":
    unittest.main()
