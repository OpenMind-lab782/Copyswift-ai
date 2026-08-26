import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioImportIntegrationTests(unittest.TestCase):

    def test_kernel_exposes_document_importer(self):
        kernel = EcosystemKernel()

        self.assertIsNotNone(kernel.document_importer)

    def test_document_studio_uses_shared_importer(self):
        kernel = EcosystemKernel()

        self.assertIs(
            kernel.document_studio.importer,
            kernel.document_importer,
        )

    def test_import_and_inspect_uses_canonical_document_model(self):
        kernel = EcosystemKernel()

        source = {
            "name": "sample.pdf",
            "pages": [
                {
                    "number": 1,
                    "width": 595,
                    "height": 842,
                    "elements": [
                        {
                            "type": "text",
                            "content": "Imported Title",
                            "x": 72,
                            "y": 72,
                            "width": 220,
                            "height": 24,
                        }
                    ],
                }
            ],
        }

        result = kernel.document_studio.import_document(source)

        self.assertEqual(result["name"], "sample.pdf")
        self.assertEqual(result["page_count"], 1)
        self.assertEqual(
            result["metadata"]["normalized"],
            True,
        )

    def test_import_does_not_mutate_source(self):
        kernel = EcosystemKernel()

        source = {
            "name": "sample.pdf",
            "pages": [
                {
                    "number": 1,
                    "width": 595,
                    "height": 842,
                    "elements": [],
                }
            ],
        }

        kernel.document_studio.import_document(source)

        self.assertEqual(
            source["pages"][0]["elements"],
            [],
        )


if __name__ == "__main__":
    unittest.main()
