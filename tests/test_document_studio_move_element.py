import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioMoveElementTests(unittest.TestCase):

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

    def test_move_element_changes_only_position(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.move_element(
            self._document(),
            element_id="text-1",
            x=150,
            y=300,
        )

        element = result["pages"][0]["elements"][0]

        self.assertEqual(element["x"], 150)
        self.assertEqual(element["y"], 300)
        self.assertEqual(element["width"], 120)
        self.assertEqual(element["height"], 20)
        self.assertEqual(element["content"], "Heading")
        self.assertEqual(element["font"], "Helvetica-Bold")
        self.assertEqual(element["font_size"], 16)
        self.assertEqual(element["color"], 0)

    def test_move_image_preserves_image_data_and_size(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.move_element(
            self._document(),
            element_id="image-1",
            x=250,
            y=350,
        )

        image = result["pages"][0]["elements"][1]

        self.assertEqual(image["x"], 250)
        self.assertEqual(image["y"], 350)
        self.assertEqual(image["width"], 200)
        self.assertEqual(image["height"], 150)
        self.assertEqual(image["image_format"], "png")
        self.assertEqual(image["image_data"], b"IMAGE-BYTES")

    def test_move_element_does_not_mutate_source(self):
        kernel = EcosystemKernel()

        original = self._document()

        kernel.document_studio.move_element(
            original,
            element_id="text-1",
            x=150,
            y=300,
        )

        element = original["pages"][0]["elements"][0]

        self.assertEqual(element["x"], 72)
        self.assertEqual(element["y"], 90)

    def test_move_element_preserves_other_elements(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.move_element(
            self._document(),
            element_id="text-1",
            x=150,
            y=300,
        )

        image = result["pages"][0]["elements"][1]

        self.assertEqual(image["x"], 100)
        self.assertEqual(image["y"], 200)
        self.assertEqual(image["image_data"], b"IMAGE-BYTES")


if __name__ == "__main__":
    unittest.main()
