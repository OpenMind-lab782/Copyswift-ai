import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioAddTextTests(unittest.TestCase):

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

    def test_add_text_preserves_existing_elements(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.add_text(
            self._document(),
            page_number=1,
            element_id="subtitle",
            content="New Subtitle",
            x=72,
            y=110,
            width=220,
            height=20,
        )

        elements = result["pages"][0]["elements"]

        self.assertEqual(len(elements), 2)
        self.assertEqual(elements[0]["content"], "Original Title")
        self.assertEqual(elements[1]["content"], "New Subtitle")

    def test_add_text_preserves_page_geometry(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.add_text(
            self._document(),
            page_number=1,
            element_id="subtitle",
            content="New Subtitle",
            x=72,
            y=110,
            width=220,
            height=20,
        )

        page = result["pages"][0]

        self.assertEqual(page["width"], 595)
        self.assertEqual(page["height"], 842)

    def test_added_text_contains_position_and_size(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.add_text(
            self._document(),
            page_number=1,
            element_id="subtitle",
            content="New Subtitle",
            x=72,
            y=110,
            width=220,
            height=20,
        )

        added = result["pages"][0]["elements"][1]

        self.assertEqual(added["id"], "subtitle")
        self.assertEqual(added["type"], "text")
        self.assertEqual(added["content"], "New Subtitle")
        self.assertEqual(added["x"], 72)
        self.assertEqual(added["y"], 110)
        self.assertEqual(added["width"], 220)
        self.assertEqual(added["height"], 20)

    def test_add_text_does_not_mutate_source(self):
        kernel = EcosystemKernel()

        original = self._document()

        result = kernel.document_studio.add_text(
            original,
            page_number=1,
            element_id="subtitle",
            content="New Subtitle",
            x=72,
            y=110,
            width=220,
            height=20,
        )

        self.assertEqual(
            len(original["pages"][0]["elements"]),
            1,
        )
        self.assertEqual(
            len(result["pages"][0]["elements"]),
            2,
        )


if __name__ == "__main__":
    unittest.main()
