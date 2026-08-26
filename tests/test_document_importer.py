import unittest

from ecosystem_core.document_importer import DocumentImporter


class DocumentImporterTests(unittest.TestCase):

    def test_importer_initializes(self):
        importer = DocumentImporter()

        self.assertIsNotNone(importer)

    def test_supported_formats_are_exposed(self):
        importer = DocumentImporter()

        formats = importer.supported_formats()

        self.assertIn("pdf", formats)
        self.assertIn("docx", formats)

    def test_normalize_document_returns_canonical_structure(self):
        importer = DocumentImporter()

        source = {
            "name": "sample.pdf",
            "pages": [
                {
                    "number": 1,
                    "width": 595,
                    "height": 842,
                    "elements": [
                        {
                            "id": "title",
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

        result = importer.normalize(source)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["name"], "sample.pdf")
        self.assertEqual(result["page_count"], 1)
        self.assertIn("pages", result)
        self.assertIn("metadata", result)

    def test_normalization_is_deterministic(self):
        importer = DocumentImporter()

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

        first = importer.normalize(source)
        second = importer.normalize(source)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
