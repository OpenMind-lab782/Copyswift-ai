import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioImageDataTests(unittest.TestCase):

    def test_text_edit_preserves_image_binary_data(self):
        kernel = EcosystemKernel()

        original_image = b"ORIGINAL-IMAGE-BYTES"

        document = {
            "name": "sample.pdf",
            "pages": [
                {
                    "number": 1,
                    "width": 595,
                    "height": 842,
                    "elements": [
                        {
                            "id": "text-1",
                            "type": "text",
                            "content": "Original Heading",
                            "x": 72,
                            "y": 90,
                            "width": 168,
                            "height": 22,
                            "font": "Helvetica-Bold",
                            "font_size": 16,
                            "flags": 20,
                            "color": 0,
                        },
                        {
                            "id": "image-1",
                            "type": "image",
                            "x": 100,
                            "y": 200,
                            "width": 200,
                            "height": 150,
                            "image_format": "png",
                            "image_data": original_image,
                        },
                    ],
                }
            ],
        }

        result = kernel.document_studio.edit_text(
            document,
            element_id="text-1",
            new_content="Updated Heading",
        )

        image = result["pages"][0]["elements"][1]

        self.assertIs(
            image["image_data"],
            original_image,
        )

        self.assertEqual(
            image["image_format"],
            "png",
        )
        self.assertEqual(
            image["x"],
            100,
        )
        self.assertEqual(
            image["y"],
            200,
        )
        self.assertEqual(
            image["width"],
            200,
        )
        self.assertEqual(
            image["height"],
            150,
        )

    def test_source_document_remains_unchanged(self):
        kernel = EcosystemKernel()

        original_image = b"ORIGINAL-IMAGE-BYTES"

        document = {
            "name": "sample.pdf",
            "pages": [
                {
                    "number": 1,
                    "width": 595,
                    "height": 842,
                    "elements": [
                        {
                            "id": "text-1",
                            "type": "text",
                            "content": "Original Heading",
                            "x": 72,
                            "y": 90,
                            "width": 168,
                            "height": 22,
                        },
                        {
                            "id": "image-1",
                            "type": "image",
                            "x": 100,
                            "y": 200,
                            "width": 200,
                            "height": 150,
                            "image_data": original_image,
                        },
                    ],
                }
            ],
        }

        kernel.document_studio.edit_text(
            document,
            element_id="text-1",
            new_content="Updated Heading",
        )

        self.assertIs(
            document["pages"][0]["elements"][1]["image_data"],
            original_image,
        )


if __name__ == "__main__":
    unittest.main()
