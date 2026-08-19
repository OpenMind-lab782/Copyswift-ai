import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioEditingTests(unittest.TestCase):

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
                            "id": "body",
                            "type": "text",
                            "content": "Original body text.",
                            "x": 72,
                            "y": 120,
                            "width": 300,
                            "height": 40,
                        },
                    ],
                }
            ],
        }

    def test_edit_text_preserves_page_geometry(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.edit_text(
            self._document(),
            element_id="title",
            new_content="Updated Title",
        )

        page = result["pages"][0]

        self.assertEqual(page["width"], 595)
        self.assertEqual(page["height"], 842)

    def test_edit_text_changes_only_target_element(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.edit_text(
            self._document(),
            element_id="title",
            new_content="Updated Title",
        )

        elements = result["pages"][0]["elements"]

        self.assertEqual(
            elements[0]["content"],
            "Updated Title",
        )
        self.assertEqual(
            elements[1]["content"],
            "Original body text.",
        )

    def test_edit_text_preserves_target_position_and_size(self):
        kernel = EcosystemKernel()

        original = self._document()

        result = kernel.document_studio.edit_text(
            original,
            element_id="title",
            new_content="Updated Title",
        )

        updated = result["pages"][0]["elements"][0]
        source = original["pages"][0]["elements"][0]

        self.assertEqual(updated["x"], source["x"])
        self.assertEqual(updated["y"], source["y"])
        self.assertEqual(updated["width"], source["width"])
        self.assertEqual(updated["height"], source["height"])

    def test_edit_text_returns_new_document_without_mutating_source(self):
        kernel = EcosystemKernel()

        original = self._document()

        result = kernel.document_studio.edit_text(
            original,
            element_id="title",
            new_content="Updated Title",
        )

        self.assertEqual(
            original["pages"][0]["elements"][0]["content"],
            "Original Title",
        )
        self.assertEqual(
            result["pages"][0]["elements"][0]["content"],
            "Updated Title",
        )


if __name__ == "__main__":
    unittest.main()
