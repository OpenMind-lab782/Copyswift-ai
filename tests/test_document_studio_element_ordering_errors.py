import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioElementOrderingErrorTests(unittest.TestCase):

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
                            "image_data": b"IMAGE",
                            "x": 100,
                            "y": 200,
                            "width": 200,
                            "height": 150,
                        },
                    ],
                }
            ],
        }

    def test_forward_invalid_document_raises_type_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(TypeError):
            kernel.document_studio.move_element_forward(
                None,
                element_id="text-1",
            )

    def test_backward_unknown_element_raises_key_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(KeyError):
            kernel.document_studio.move_element_backward(
                self._document(),
                element_id="missing",
            )

    def test_to_front_unknown_element_raises_key_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(KeyError):
            kernel.document_studio.move_element_to_front(
                self._document(),
                element_id="missing",
            )

    def test_to_back_unknown_element_raises_key_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(KeyError):
            kernel.document_studio.move_element_to_back(
                self._document(),
                element_id="missing",
            )


if __name__ == "__main__":
    unittest.main()
