import unittest

from ecosystem_core.document_importer import DocumentImporter


class DocumentImporterImageDataTests(unittest.TestCase):

    def test_image_binary_data_survives_normalization(self):
        importer = DocumentImporter()

        original_bytes = b"ORIGINAL-IMAGE-BYTES"

        source = {
            "name": "image.pdf",
            "pages": [
                {
                    "number": 1,
                    "width": 595,
                    "height": 842,
                    "elements": [
                        {
                            "id": "image-1",
                            "type": "image",
                            "x": 100,
                            "y": 200,
                            "width": 200,
                            "height": 150,
                            "image_format": "png",
                            "xres": 96,
                            "yres": 96,
                            "image_data": original_bytes,
                        }
                    ],
                }
            ],
        }

        result = importer.normalize(source)

        image = result["pages"][0]["elements"][0]

        self.assertIs(
            image["image_data"],
            original_bytes,
        )

    def test_image_data_does_not_change_across_repeated_normalization(self):
        importer = DocumentImporter()

        source = {
            "name": "image.pdf",
            "pages": [
                {
                    "number": 1,
                    "width": 595,
                    "height": 842,
                    "elements": [
                        {
                            "id": "image-1",
                            "type": "image",
                            "x": 100,
                            "y": 200,
                            "width": 200,
                            "height": 150,
                            "image_format": "png",
                            "image_data": b"IMAGE-BYTES",
                        }
                    ],
                }
            ],
        }

        first = importer.normalize(source)
        second = importer.normalize(source)

        self.assertEqual(
            first["pages"][0]["elements"][0]["image_data"],
            second["pages"][0]["elements"][0]["image_data"],
        )

    def test_source_document_is_not_mutated(self):
        importer = DocumentImporter()

        original_bytes = b"IMAGE-BYTES"

        source = {
            "name": "image.pdf",
            "pages": [
                {
                    "number": 1,
                    "width": 595,
                    "height": 842,
                    "elements": [
                        {
                            "id": "image-1",
                            "type": "image",
                            "x": 100,
                            "y": 200,
                            "width": 200,
                            "height": 150,
                            "image_data": original_bytes,
                        }
                    ],
                }
            ],
        }

        importer.normalize(source)

        self.assertIs(
            source["pages"][0]["elements"][0]["image_data"],
            original_bytes,
        )


if __name__ == "__main__":
    unittest.main()
