import unittest

from ecosystem_core.document_renderer import DocumentRenderer
from ecosystem_core.document_renderers.pymupdf_renderer import PyMuPDFRenderer
from ecosystem_core.kernel import EcosystemKernel


class DocumentRendererEngineInjectionTests(unittest.TestCase):

    def test_kernel_can_use_pymupdf_renderer_engine(self):
        kernel = EcosystemKernel()
        engine = PyMuPDFRenderer()

        kernel.document_renderer.engine = engine

        self.assertIs(
            kernel.document_renderer.engine,
            engine,
        )

    def test_document_studio_uses_same_renderer_after_engine_injection(self):
        kernel = EcosystemKernel()
        engine = PyMuPDFRenderer()

        kernel.document_renderer.engine = engine

        self.assertIs(
            kernel.document_studio.renderer,
            kernel.document_renderer,
        )
        self.assertIs(
            kernel.document_studio.renderer.engine,
            engine,
        )

    def test_renderer_engine_is_optional(self):
        renderer = DocumentRenderer()

        self.assertIsNone(
            renderer.engine,
        )

        with self.assertRaises(RuntimeError):
            renderer.render(
                {
                    "name": "sample.pdf",
                    "pages": [],
                }
            )


if __name__ == "__main__":
    unittest.main()
