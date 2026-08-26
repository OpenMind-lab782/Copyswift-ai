import unittest

from ecosystem_core.document_renderers.pymupdf_renderer import PyMuPDFRenderer


class PyMuPDFRendererTests(unittest.TestCase):

    def test_renderer_initializes(self):
        renderer = PyMuPDFRenderer()

        self.assertIsNotNone(renderer)

    def test_renderer_exposes_render_method(self):
        renderer = PyMuPDFRenderer()

        self.assertTrue(
            callable(renderer.render)
        )

    def test_renderer_reports_engine_unavailable_cleanly(self):
        renderer = PyMuPDFRenderer()

        with self.assertRaises(RuntimeError) as context:
            renderer.render(
                {
                    "name": "sample.pdf",
                    "pages": [],
                },
                output_name="output.pdf",
            )

        self.assertIn(
            "PyMuPDF",
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()
