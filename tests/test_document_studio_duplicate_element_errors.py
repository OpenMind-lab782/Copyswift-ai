import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioDuplicateElementErrorTests(unittest.TestCase):

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

    def test_invalid_document_raises_type_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(TypeError):
            kernel.document_studio.duplicate_element(
                None,
                element_id="text-1",
                new_element_id="text-2",
                x=200,
                y=300,
            )

    def test_missing_source_element_raises_key_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(KeyError):
            kernel.document_studio.duplicate_element(
                self._document(),
                element_id="missing",
                new_element_id="text-2",
                x=200,
                y=300,
            )

    def test_existing_target_id_raises_value_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(ValueError):
            kernel.document_studio.duplicate_element(
                self._document(),
                element_id="text-1",
                new_element_id="text-1",
                x=200,
                y=300,
            )


if __name__ == "__main__":
    unittest.main()
