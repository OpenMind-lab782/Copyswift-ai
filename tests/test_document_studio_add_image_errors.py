import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioAddImageErrorTests(unittest.TestCase):

    def _document(self):
        return {
            "name": "sample.pdf",
            "pages": [
                {
                    "number": 1,
                    "width": 595,
                    "height": 842,
                    "elements": [],
                }
            ],
        }

    def test_invalid_document_raises_type_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(TypeError):
            kernel.document_studio.add_image(
                None,
                page_number=1,
                element_id="image-1",
                image_data=b"IMAGE",
                x=100,
                y=200,
                width=200,
                height=150,
            )

    def test_missing_page_raises_key_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(KeyError):
            kernel.document_studio.add_image(
                self._document(),
                page_number=99,
                element_id="image-1",
                image_data=b"IMAGE",
                x=100,
                y=200,
                width=200,
                height=150,
            )

    def test_duplicate_element_id_raises_value_error(self):
        kernel = EcosystemKernel()

        document = self._document()
        document["pages"][0]["elements"].append(
            {
                "id": "image-1",
                "type": "image",
                "image_data": b"ORIGINAL",
                "x": 10,
                "y": 10,
                "width": 50,
                "height": 50,
            }
        )

        with self.assertRaises(ValueError):
            kernel.document_studio.add_image(
                document,
                page_number=1,
                element_id="image-1",
                image_data=b"UPDATED",
                x=100,
                y=200,
                width=200,
                height=150,
            )


if __name__ == "__main__":
    unittest.main()
