import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioDuplicateElementTests(unittest.TestCase):

    def _document(self):
        return {
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
                            "content": "Heading",
                            "x": 72,
                            "y": 90,
                            "width": 120,
                            "height": 20,
                            "font": "Helvetica-Bold",
                            "font_size": 16,
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
                            "image_data": b"IMAGE-BYTES",
                        },
                    ],
                }
            ],
        }

    def test_duplicate_text_creates_new_element(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.duplicate_element(
            self._document(),
            element_id="text-1",
            new_element_id="text-2",
            x=200,
            y=300,
        )

        elements = result["pages"][0]["elements"]

        self.assertEqual(len(elements), 3)

        duplicate = elements[2]

        self.assertEqual(duplicate["id"], "text-2")
        self.assertEqual(duplicate["type"], "text")
        self.assertEqual(duplicate["content"], "Heading")
        self.assertEqual(duplicate["x"], 200)
        self.assertEqual(duplicate["y"], 300)
        self.assertEqual(duplicate["width"], 120)
        self.assertEqual(duplicate["height"], 20)
        self.assertEqual(duplicate["font"], "Helvetica-Bold")
        self.assertEqual(duplicate["font_size"], 16)
        self.assertEqual(duplicate["color"], 0)

    def test_duplicate_image_preserves_binary_data_and_geometry(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.duplicate_element(
            self._document(),
            element_id="image-1",
            new_element_id="image-2",
            x=250,
            y=350,
        )

        elements = result["pages"][0]["elements"]
        duplicate = elements[2]

        self.assertEqual(duplicate["id"], "image-2")
        self.assertEqual(duplicate["type"], "image")
        self.assertEqual(duplicate["x"], 250)
        self.assertEqual(duplicate["y"], 350)
        self.assertEqual(duplicate["width"], 200)
        self.assertEqual(duplicate["height"], 150)
        self.assertEqual(duplicate["image_format"], "png")
        self.assertEqual(duplicate["image_data"], b"IMAGE-BYTES")

    def test_duplicate_does_not_modify_original(self):
        kernel = EcosystemKernel()

        original = self._document()

        result = kernel.document_studio.duplicate_element(
            original,
            element_id="text-1",
            new_element_id="text-2",
            x=200,
            y=300,
        )

        self.assertEqual(
            len(original["pages"][0]["elements"]),
            2,
        )

        self.assertEqual(
            len(result["pages"][0]["elements"]),
            3,
        )

    def test_original_element_remains_unchanged(self):
        kernel = EcosystemKernel()

        original = self._document()

        result = kernel.document_studio.duplicate_element(
            original,
            element_id="text-1",
            new_element_id="text-2",
            x=200,
            y=300,
        )

        original_element = result["pages"][0]["elements"][0]

        self.assertEqual(original_element["id"], "text-1")
        self.assertEqual(original_element["x"], 72)
        self.assertEqual(original_element["y"], 90)
        self.assertEqual(original_element["content"], "Heading")

    def test_duplicate_rejects_existing_new_id(self):
        kernel = EcosystemKernel()

        with self.assertRaises(ValueError):
            kernel.document_studio.duplicate_element(
                self._document(),
                element_id="text-1",
                new_element_id="image-1",
                x=200,
                y=300,
            )


if __name__ == "__main__":
    unittest.main()
