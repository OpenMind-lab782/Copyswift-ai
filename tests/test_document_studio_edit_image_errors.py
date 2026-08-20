import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioEditImageErrorTests(unittest.TestCase):

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
                            "image_data": b"ORIGINAL",
                        },
                        {
                            "id": "text-1",
                            "type": "text",
                            "content": "Heading",
                            "x": 72,
                            "y": 90,
                            "width": 100,
                            "height": 20,
                        },
                    ],
                }
            ],
        }

    def test_invalid_document_raises_type_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(TypeError):
            kernel.document_studio.edit_image(
                None,
                element_id="image-1",
                image_data=b"UPDATED",
            )

    def test_unknown_element_id_raises_key_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(KeyError):
            kernel.document_studio.edit_image(
                self._document(),
                element_id="missing-image",
                image_data=b"UPDATED",
            )

    def test_non_image_element_raises_value_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(ValueError):
            kernel.document_studio.edit_image(
                self._document(),
                element_id="text-1",
                image_data=b"UPDATED",
            )


if __name__ == "__main__":
    unittest.main()
