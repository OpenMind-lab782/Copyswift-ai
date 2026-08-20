import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioDeleteElementTests(unittest.TestCase):

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
                        },
                        {
                            "id": "image-1",
                            "type": "image",
                            "image_data": b"IMAGE-BYTES",
                            "x": 100,
                            "y": 200,
                            "width": 200,
                            "height": 150,
                        },
                    ],
                }
            ],
        }

    def test_delete_element_removes_only_target(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.delete_element(
            self._document(),
            element_id="text-1",
        )

        elements = result["pages"][0]["elements"]

        self.assertEqual(
            len(elements),
            1,
        )
        self.assertEqual(
            elements[0]["id"],
            "image-1",
        )

    def test_delete_image_preserves_remaining_element(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.delete_element(
            self._document(),
            element_id="image-1",
        )

        elements = result["pages"][0]["elements"]

        self.assertEqual(
            len(elements),
            1,
        )
        self.assertEqual(
            elements[0]["id"],
            "text-1",
        )
        self.assertEqual(
            elements[0]["content"],
            "Heading",
        )

    def test_delete_element_does_not_mutate_source(self):
        kernel = EcosystemKernel()

        original = self._document()

        kernel.document_studio.delete_element(
            original,
            element_id="text-1",
        )

        self.assertEqual(
            len(original["pages"][0]["elements"]),
            2,
        )

    def test_delete_element_preserves_remaining_image_data(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.delete_element(
            self._document(),
            element_id="text-1",
        )

        image = result["pages"][0]["elements"][0]

        self.assertEqual(
            image["image_data"],
            b"IMAGE-BYTES",
        )


if __name__ == "__main__":
    unittest.main()
