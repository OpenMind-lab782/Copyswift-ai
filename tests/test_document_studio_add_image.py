import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioAddImageTests(unittest.TestCase):

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
                            "content": "Existing Heading",
                            "x": 72,
                            "y": 90,
                            "width": 150,
                            "height": 20,
                        }
                    ],
                }
            ],
        }

    def test_add_image_creates_positioned_image_element(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.add_image(
            self._document(),
            page_number=1,
            element_id="image-1",
            image_data=b"NEW-IMAGE",
            x=100,
            y=200,
            width=200,
            height=150,
            image_format="png",
        )

        image = result["pages"][0]["elements"][1]

        self.assertEqual(image["id"], "image-1")
        self.assertEqual(image["type"], "image")
        self.assertEqual(image["image_data"], b"NEW-IMAGE")
        self.assertEqual(image["image_format"], "png")
        self.assertEqual(image["x"], 100)
        self.assertEqual(image["y"], 200)
        self.assertEqual(image["width"], 200)
        self.assertEqual(image["height"], 150)

    def test_add_image_preserves_existing_elements(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.add_image(
            self._document(),
            page_number=1,
            element_id="image-1",
            image_data=b"NEW-IMAGE",
            x=100,
            y=200,
            width=200,
            height=150,
            image_format="png",
        )

        self.assertEqual(
            result["pages"][0]["elements"][0]["content"],
            "Existing Heading",
        )

    def test_add_image_does_not_mutate_source(self):
        kernel = EcosystemKernel()

        original = self._document()

        kernel.document_studio.add_image(
            original,
            page_number=1,
            element_id="image-1",
            image_data=b"NEW-IMAGE",
            x=100,
            y=200,
            width=200,
            height=150,
            image_format="png",
        )

        self.assertEqual(
            len(original["pages"][0]["elements"]),
            1,
        )

    def test_add_image_rejects_duplicate_element_id(self):
        kernel = EcosystemKernel()

        with self.assertRaises(ValueError):
            kernel.document_studio.add_image(
                self._document(),
                page_number=1,
                element_id="text-1",
                image_data=b"NEW-IMAGE",
                x=100,
                y=200,
                width=200,
                height=150,
                image_format="png",
            )


if __name__ == "__main__":
    unittest.main()
