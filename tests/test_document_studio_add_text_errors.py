import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioAddTextErrorTests(unittest.TestCase):

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
                        }
                    ],
                }
            ],
        }

    def test_duplicate_element_id_raises_value_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(ValueError):
            kernel.document_studio.add_text(
                self._document(),
                page_number=1,
                element_id="title",
                content="Duplicate",
                x=72,
                y=110,
                width=220,
                height=20,
            )

    def test_missing_page_raises_key_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(KeyError):
            kernel.document_studio.add_text(
                self._document(),
                page_number=2,
                element_id="subtitle",
                content="New Subtitle",
                x=72,
                y=110,
                width=220,
                height=20,
            )

    def test_invalid_document_raises_type_error(self):
        kernel = EcosystemKernel()

        with self.assertRaises(TypeError):
            kernel.document_studio.add_text(
                None,
                page_number=1,
                element_id="subtitle",
                content="New Subtitle",
                x=72,
                y=110,
                width=220,
                height=20,
            )


if __name__ == "__main__":
    unittest.main()
