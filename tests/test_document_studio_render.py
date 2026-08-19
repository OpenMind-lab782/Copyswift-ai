import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioRenderTests(unittest.TestCase):

    def test_document_studio_exposes_render_document(self):
        kernel = EcosystemKernel()

        self.assertTrue(
            callable(kernel.document_studio.render_document)
        )

    def test_render_document_delegates_to_shared_renderer(self):
        kernel = EcosystemKernel()

        captured = {}

        class FakeRenderer:
            def render(self, document, output_name="output.pdf"):
                captured["document"] = document
                captured["output_name"] = output_name
                return b"%PDF-rendered%"

        kernel.document_studio.renderer = FakeRenderer()

        document = {
            "name": "sample.pdf",
            "pages": [],
        }

        result = kernel.document_studio.render_document(
            document,
            output_name="edited.pdf",
        )

        self.assertEqual(
            result,
            b"%PDF-rendered%",
        )
        self.assertIs(
            captured["document"],
            document,
        )
        self.assertEqual(
            captured["output_name"],
            "edited.pdf",
        )

    def test_render_document_requires_renderer(self):
        kernel = EcosystemKernel()
        kernel.document_studio.renderer = None

        with self.assertRaises(RuntimeError):
            kernel.document_studio.render_document(
                {
                    "name": "sample.pdf",
                    "pages": [],
                }
            )


if __name__ == "__main__":
    unittest.main()
