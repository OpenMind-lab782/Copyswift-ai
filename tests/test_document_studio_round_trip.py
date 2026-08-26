import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioRoundTripTests(unittest.TestCase):

    def test_import_binary_document_exposes_editable_document(self):
        kernel = EcosystemKernel()

        class FakeParser:
            def parse(self, data, file_name):
                return {
                    "name": file_name,
                    "pages": [
                        {
                            "number": 1,
                            "width": 595,
                            "height": 842,
                            "elements": [
                                {
                                    "id": "text-1",
                                    "type": "text",
                                    "content": "Original",
                                    "x": 72,
                                    "y": 90,
                                    "width": 100,
                                    "height": 20,
                                }
                            ],
                        }
                    ],
                }

        kernel.document_studio.parser = FakeParser()

        result = kernel.document_studio.import_binary_document(
            b"fake-pdf",
            file_name="sample.pdf",
        )

        self.assertEqual(
            result["name"],
            "sample.pdf",
        )
        self.assertEqual(
            result["pages"][0]["elements"][0]["content"],
            "Original",
        )

    def test_import_binary_document_requires_parser(self):
        kernel = EcosystemKernel()
        kernel.document_studio.parser = None

        with self.assertRaises(RuntimeError):
            kernel.document_studio.import_binary_document(
                b"fake-pdf",
                file_name="sample.pdf",
            )

    def test_export_document_delegates_to_shared_renderer(self):
        kernel = EcosystemKernel()

        captured = {}

        class FakeRenderer:
            def render(self, document, output_name="output.pdf"):
                captured["document"] = document
                captured["output_name"] = output_name
                return b"%PDF-round-trip%"

        kernel.document_studio.renderer = FakeRenderer()

        document = {
            "name": "sample.pdf",
            "pages": [],
        }

        result = kernel.document_studio.export_document(
            document,
            output_name="edited.pdf",
        )

        self.assertEqual(
            result,
            b"%PDF-round-trip%",
        )
        self.assertIs(
            captured["document"],
            document,
        )
        self.assertEqual(
            captured["output_name"],
            "edited.pdf",
        )

    def test_export_document_requires_renderer(self):
        kernel = EcosystemKernel()
        kernel.document_studio.renderer = None

        with self.assertRaises(RuntimeError):
            kernel.document_studio.export_document(
                {
                    "name": "sample.pdf",
                    "pages": [],
                }
            )


if __name__ == "__main__":
    unittest.main()
