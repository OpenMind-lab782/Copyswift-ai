import unittest

from ecosystem_core.document_renderer import DocumentRenderer


class DocumentRendererTests(unittest.TestCase):

    def test_renderer_initializes(self):
        renderer = DocumentRenderer()

        self.assertIsNotNone(renderer)

    def test_renderer_exposes_render_contract(self):
        renderer = DocumentRenderer()

        self.assertTrue(
            callable(renderer.render)
        )

    def test_renderer_rejects_invalid_document(self):
        renderer = DocumentRenderer()

        with self.assertRaises(TypeError):
            renderer.render(
                None,
                output_name="output.pdf",
            )


if __name__ == "__main__":
    unittest.main()
