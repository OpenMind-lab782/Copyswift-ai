import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioElementOrderingTests(unittest.TestCase):

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

    def test_move_element_forward_reorders_only_target(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.move_element_forward(
            self._document(),
            element_id="text-1",
        )

        ids = [
            element["id"]
            for element in result["pages"][0]["elements"]
        ]

        self.assertEqual(
            ids,
            ["text-2", "text-1", "image-1"],
        )

    def test_move_element_backward_reorders_only_target(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.move_element_backward(
            self._document(),
            element_id="image-1",
        )

        ids = [
            element["id"]
            for element in result["pages"][0]["elements"]
        ]

        self.assertEqual(
            ids,
            ["text-1", "image-1", "text-2"],
        )

    def test_move_element_to_front_places_target_last(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.move_element_to_front(
            self._document(),
            element_id="text-1",
        )

        ids = [
            element["id"]
            for element in result["pages"][0]["elements"]
        ]

        self.assertEqual(
            ids,
            ["text-2", "image-1", "text-1"],
        )

    def test_move_element_to_back_places_target_first(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.move_element_to_back(
            self._document(),
            element_id="image-1",
        )

        ids = [
            element["id"]
            for element in result["pages"][0]["elements"]
        ]

        self.assertEqual(
            ids,
            ["image-1", "text-1", "text-2"],
        )

    def test_ordering_does_not_mutate_source(self):
        kernel = EcosystemKernel()

        original = self._document()

        kernel.document_studio.move_element_forward(
            original,
            element_id="text-1",
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
