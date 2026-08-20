import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioDuplicateAndOrderTests(unittest.TestCase):

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
                            "content": "One",
                            "x": 10,
                            "y": 10,
                            "width": 50,
                            "height": 20,
                        },
                        {
                            "id": "text-2",
                            "type": "text",
                            "content": "Two",
                            "x": 20,
                            "y": 20,
                            "width": 50,
                            "height": 20,
                        },
                        {
                            "id": "image-1",
                            "type": "image",
                            "image_data": b"IMAGE",
                            "x": 30,
                            "y": 30,
                            "width": 100,
                            "height": 100,
                        },
                    ],
                }
            ],
        }

    def test_duplicate_then_move_to_front(self):
        kernel = EcosystemKernel()

        duplicated = kernel.document_studio.duplicate_element(
            self._document(),
            element_id="text-1",
            new_element_id="text-copy",
            x=200,
            y=300,
        )

        reordered = kernel.document_studio.move_element_to_front(
            duplicated,
            element_id="text-copy",
        )

        ids = [
            element["id"]
            for element in reordered["pages"][0]["elements"]
        ]

        self.assertEqual(
            ids,
            ["text-1", "text-2", "image-1", "text-copy"],
        )

    def test_duplicate_then_move_backward_preserves_original(self):
        kernel = EcosystemKernel()

        duplicated = kernel.document_studio.duplicate_element(
            self._document(),
            element_id="image-1",
            new_element_id="image-copy",
            x=200,
            y=300,
        )

        reordered = kernel.document_studio.move_element_backward(
            duplicated,
            element_id="image-copy",
        )

        ids = [
            element["id"]
            for element in reordered["pages"][0]["elements"]
        ]

        self.assertEqual(
            ids,
            ["text-1", "text-2", "image-copy", "image-1"],
        )

        original = next(
            element
            for element in reordered["pages"][0]["elements"]
            if element["id"] == "image-1"
        )

        duplicate = next(
            element
            for element in reordered["pages"][0]["elements"]
            if element["id"] == "image-copy"
        )

        self.assertEqual(
            original["image_data"],
            b"IMAGE",
        )

        self.assertEqual(
            duplicate["image_data"],
            b"IMAGE",
        )
        self.assertEqual(
            duplicate["x"],
            200,
        )
        self.assertEqual(
            duplicate["y"],
            300,
        )

    def test_duplicate_and_ordering_leave_source_unchanged(self):
        kernel = EcosystemKernel()

        original = self._document()

        duplicated = kernel.document_studio.duplicate_element(
            original,
            element_id="text-1",
            new_element_id="text-copy",
            x=200,
            y=300,
        )

        kernel.document_studio.move_element_to_front(
            duplicated,
            element_id="text-copy",
        )

        ids = [
            element["id"]
            for element in original["pages"][0]["elements"]
        ]

        self.assertEqual(
            ids,
            ["text-1", "text-2", "image-1"],
        )


if __name__ == "__main__":
    unittest.main()
