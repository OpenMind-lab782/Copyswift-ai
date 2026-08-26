import unittest

from ecosystem_core.kernel import EcosystemKernel
from ecosystem_core.document_studio import DocumentStudio


class DocumentStudioFoundationTests(unittest.TestCase):

    def test_document_studio_initializes(self):
        kernel = EcosystemKernel()

        studio = DocumentStudio()

        self.assertIsNotNone(studio)

    def test_kernel_exposes_document_studio(self):
        kernel = EcosystemKernel()

        self.assertIsNotNone(kernel.document_studio)

    def test_document_studio_product_is_registered(self):
        kernel = EcosystemKernel()

        product = kernel.products.get("document_studio")

        self.assertIsInstance(product, dict)
        self.assertEqual(product["status"], "planned")

    def test_inspect_document_returns_expected_structure(self):
        kernel = EcosystemKernel()

        document = {
            "name": "sample.pdf",
            "pages": [
                {
                    "number": 1,
                    "width": 595,
                    "height": 842,
                    "elements": [
                        {
                            "type": "text",
                            "content": "Sample Document",
                            "x": 72,
                            "y": 72,
                            "width": 220,
                            "height": 24,
                        }
                    ],
                }
            ],
        }

        result = kernel.document_studio.inspect_document(document)

        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertIn("page_count", result)
        self.assertIn("pages", result)
        self.assertIn("structure", result)

        self.assertEqual(result["page_count"], 1)
        self.assertEqual(result["pages"][0]["number"], 1)


if __name__ == "__main__":
    unittest.main()
