import unittest

from ecosystem_core.document_parser import DocumentParser


class DocumentParserAdapterTests(unittest.TestCase):

    def test_parser_initializes(self):
        parser = DocumentParser()

        self.assertIsNotNone(parser)

    def test_parser_exposes_supported_formats(self):
        parser = DocumentParser()

        formats = parser.supported_formats()

        self.assertIn("pdf", formats)
        self.assertIn("docx", formats)

    def test_parser_has_parse_contract(self):
        parser = DocumentParser()

        self.assertTrue(
            callable(parser.parse)
        )

    def test_parser_rejects_unsupported_format(self):
        parser = DocumentParser()

        with self.assertRaises(ValueError):
            parser.parse(
                b"sample",
                file_name="sample.xyz",
            )


if __name__ == "__main__":
    unittest.main()
