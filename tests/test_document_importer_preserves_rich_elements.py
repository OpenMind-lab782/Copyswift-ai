import unittest

from ecosystem_core.document_importer import DocumentImporter


class DocumentImporterRichElementTests(unittest.TestCase):

    def test_text_style_metadata_is_preserved(self):
        importer = DocumentImporter()

        source = {
            "name": "styled.pdf",
            "pages": [
                {
                    "number": 1,
                    "width": 595,
                    "height": 842,
                    "elements": [
                        {
                            "id": "text-1",
                            "type": "text",
                            "content": "Styled Heading",
                            "x": 72,
                            "y": 90,
                            "width": 168,
                            "height": 22,
                            "font": "Helvetica-Bold",
                            "font_size": 16,
                            "flags": 20,
                            "color": 0,
                        }
                    ],
                }
            ],
        }

        result = importer.normalize(source)
        element = result["pages"][0]["elements"][0]

        self.assertEqual(element["font"], "Helvetica-Bold")
        self.assertEqual(element["font_size"], 16)
        self.assertEqual(element["flags"], 20)
        self.assertEqual(element["color"], 0)

    def test_image_metadata_is_preserved(self):
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
                            "xres": 96,
                            "yres": 96,
                        }
                    ],
                }
            ],
        }

        result = importer.normalize(source)
        element = result["pages"][0]["elements"][0]

        self.assertEqual(element["type"], "image")
        self.assertEqual(element["image_format"], "png")
        self.assertEqual(element["xres"], 96)
        self.assertEqual(element["yres"], 96)

    def test_rich_elements_remain_deterministic(self):
        importer = DocumentImporter()

        source = {
            "name": "rich.pdf",
            "pages": [
                {
                    "number": 1,
                    "width": 595,
                    "height": 842,
                    "elements": [
                        {
                            "id": "text-1",
                            "type": "text",
                            "content": "Hello",
                            "x": 72,
                            "y": 90,
                            "width": 50,
                            "height": 15,
                            "font": "Helvetica",
                            "font_size": 12,
                        }
                    ],
                }
            ],
        }

        first = importer.normalize(source)
        second = importer.normalize(source)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
