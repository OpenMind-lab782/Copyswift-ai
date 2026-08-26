import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioEditingErrorTests(unittest.TestCase):

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
                            "id": "title",
                            "type": "text",
                            "content": "Original Title",
                            "x": 72,
                            "y": 72,
                            "width": 220,
                            "height": 24,
                        },
                        {
                            "id": "image-1",
                            "type": "image",
                            "content": "image-data",
                            "x": 100,
                            "y": 200,
                            "width": 300,
                            "height": 200,
                        },
                    ],
                }
            ],
        }

    def test_unknown_element_id_raises_key_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(KeyError):
            kernel.document_studio.edit_text(
                self._document(),
                element_id="missing",
                new_content="Updated",
            )

    def test_non_text_element_raises_value_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(ValueError):
            kernel.document_studio.edit_text(
                self._document(),
                element_id="image-1",
                new_content="Updated",
            )

    def test_invalid_document_raises_type_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(TypeError):
            kernel.document_studio.edit_text(
                None,
                element_id="title",
                new_content="Updated",
            )


if __name__ == "__main__":
    unittest.main()
