import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioEditImageTests(unittest.TestCase):

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
                            "id": "image-1",
                            "type": "image",
                            "x": 100,
                            "y": 200,
                            "width": 200,
                            "height": 150,
                            "image_format": "png",
                            "image_data": b"ORIGINAL-IMAGE",
                        }
                    ],
                }
            ],
        }

    def test_edit_image_replaces_binary_data(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.edit_image(
            self._document(),
            element_id="image-1",
            image_data=b"UPDATED-IMAGE",
        )

        image = result["pages"][0]["elements"][0]

        self.assertEqual(
            image["image_data"],
            b"UPDATED-IMAGE",
        )

    def test_edit_image_preserves_geometry(self):
        kernel = EcosystemKernel()

        original = self._document()

        result = kernel.document_studio.edit_image(
            original,
            element_id="image-1",
            image_data=b"UPDATED-IMAGE",
        )

        image = result["pages"][0]["elements"][0]

        self.assertEqual(image["x"], 100)
        self.assertEqual(image["y"], 200)
        self.assertEqual(image["width"], 200)
        self.assertEqual(image["height"], 150)

    def test_edit_image_preserves_image_metadata(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.edit_image(
            self._document(),
            element_id="image-1",
            image_data=b"UPDATED-IMAGE",
        )

        image = result["pages"][0]["elements"][0]

        self.assertEqual(
            image["image_format"],
            "png",
        )

    def test_edit_image_does_not_mutate_source(self):
        kernel = EcosystemKernel()

        original = self._document()

        kernel.document_studio.edit_image(
            original,
            element_id="image-1",
            image_data=b"UPDATED-IMAGE",
        )

        self.assertEqual(
            original["pages"][0]["elements"][0]["image_data"],
            b"ORIGINAL-IMAGE",
        )


if __name__ == "__main__":
    unittest.main()
