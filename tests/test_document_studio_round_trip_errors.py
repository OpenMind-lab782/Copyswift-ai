import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioRoundTripErrorTests(unittest.TestCase):

    def test_import_binary_document_rejects_unsupported_format(self):
        kernel = EcosystemKernel()

        with self.assertRaises(ValueError):
            kernel.document_studio.import_binary_document(
                b"fake-data",
                file_name="sample.xyz",
            )

    def test_import_binary_document_propagates_parser_failure(self):
        kernel = EcosystemKernel()

        class FailingParser:
            def parse(self, data, file_name):
                raise RuntimeError("Parser failed.")

        kernel.document_studio.parser = FailingParser()

        with self.assertRaises(RuntimeError) as context:
            kernel.document_studio.import_binary_document(
                b"fake-data",
                file_name="sample.pdf",
            )

        self.assertIn(
            "Parser failed.",
            str(context.exception),
        )

    def test_export_document_propagates_renderer_failure(self):
        kernel = EcosystemKernel()

        class FailingRenderer:
            def render(self, document, output_name="output.pdf"):
                raise RuntimeError("Renderer failed.")

        kernel.document_studio.renderer = FailingRenderer()

        with self.assertRaises(RuntimeError) as context:
            kernel.document_studio.export_document(
                {
                    "name": "sample.pdf",
                    "pages": [],
                },
                output_name="edited.pdf",
            )

        self.assertIn(
            "Renderer failed.",
            str(context.exception),
        )

    def test_export_document_rejects_invalid_document(self):
        kernel = EcosystemKernel()

        class FakeRenderer:
            def render(self, document, output_name="output.pdf"):
                if not isinstance(document, dict):
                    raise TypeError("Document must be a dictionary.")
                return b"%PDF%"

        kernel.document_studio.renderer = FakeRenderer()

        with self.assertRaises(TypeError):
            kernel.document_studio.export_document(
                None,
                output_name="edited.pdf",
            )


if __name__ == "__main__":
    unittest.main()
