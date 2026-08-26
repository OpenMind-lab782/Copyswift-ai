import unittest

from ecosystem_core.document_importer import DocumentImporter
from ecosystem_core.document_parser import DocumentParser


class FakePDFAdapter:
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
                            "type": "text",
                            "content": "Parsed Title",
                            "x": 72,
                            "y": 72,
                            "width": 220,
                            "height": 24,
                        }
                    ],
                }
            ],
        }


class DocumentParserImporterPipelineTests(unittest.TestCase):

    def test_parser_can_feed_importer(self):
        parser = DocumentParser(
            adapters={"pdf": FakePDFAdapter()}
        )
        importer = DocumentImporter()

        parsed = parser.parse(
            b"fake-pdf-data",
            file_name="sample.pdf",
        )

        result = importer.normalize(parsed)

        self.assertEqual(result["name"], "sample.pdf")
        self.assertEqual(result["page_count"], 1)
        self.assertEqual(
            result["pages"][0]["elements"][0]["content"],
            "Parsed Title",
        )

    def test_parser_output_can_become_canonical_document(self):
        parser = DocumentParser(
            adapters={"pdf": FakePDFAdapter()}
        )
        importer = DocumentImporter()

        parsed = parser.parse(
            b"fake-pdf-data",
            file_name="sample.pdf",
        )
        canonical = importer.normalize(parsed)

        self.assertIn("pages", canonical)
        self.assertIn("metadata", canonical)
        self.assertEqual(
            canonical["metadata"]["normalized"],
            True,
        )

    def test_importer_does_not_mutate_parser_output(self):
        parser = DocumentParser(
            adapters={"pdf": FakePDFAdapter()}
        )
        importer = DocumentImporter()

        parsed = parser.parse(
            b"fake-pdf-data",
            file_name="sample.pdf",
        )

        original = repr(parsed)

        importer.normalize(parsed)

        self.assertEqual(repr(parsed), original)


if __name__ == "__main__":
    unittest.main()
