import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioGeometryErrorTests(unittest.TestCase):

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
                        }
                    ],
                }
            ],
        }

    def test_move_invalid_document_raises_type_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(TypeError):
            kernel.document_studio.move_element(
                None,
                element_id="text-1",
                x=100,
                y=100,
            )

    def test_move_unknown_element_raises_key_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(KeyError):
            kernel.document_studio.move_element(
                self._document(),
                element_id="missing",
                x=100,
                y=100,
            )

    def test_resize_invalid_document_raises_type_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(TypeError):
            kernel.document_studio.resize_element(
                None,
                element_id="text-1",
                width=200,
                height=40,
            )

    def test_resize_unknown_element_raises_key_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(KeyError):
            kernel.document_studio.resize_element(
                self._document(),
                element_id="missing",
                width=200,
                height=40,
            )


if __name__ == "__main__":
    unittest.main()
