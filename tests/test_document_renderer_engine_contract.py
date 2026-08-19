import unittest

from ecosystem_core.document_renderer import DocumentRenderer


class DocumentRendererEngineContractTests(unittest.TestCase):

    def test_renderer_uses_configured_engine(self):
        captured = {}

        class FakeEngine:
            def render(self, document, output_name):
                captured["document"] = document
                captured["output_name"] = output_name
                return b"%PDF-fake%"

        renderer = DocumentRenderer(
            engine=FakeEngine()
        )

        document = {
            "name": "sample.pdf",
            "pages": [],
        }

        result = renderer.render(
            document,
            output_name="edited.pdf",
        )

        self.assertEqual(
            result,
            b"%PDF-fake%",
        )
        self.assertIs(
            captured["document"],
            document,
        )
        self.assertEqual(
            captured["output_name"],
            "edited.pdf",
        )

    def test_renderer_propagates_engine_failures(self):
        class FailingEngine:
            def render(self, document, output_name):
                raise RuntimeError(
                    "PDF rendering engine unavailable."
                )

        renderer = DocumentRenderer(
            engine=FailingEngine()
        )

        with self.assertRaises(RuntimeError):
            renderer.render(
                {
                    "name": "sample.pdf",
                    "pages": [],
                }
            )

    def test_renderer_requires_engine_for_valid_document(self):
        renderer = DocumentRenderer()

        with self.assertRaises(RuntimeError):
            renderer.render(
                {
                    "name": "sample.pdf",
                    "pages": [],
                }
            )


if __name__ == "__main__":
    unittest.main()
