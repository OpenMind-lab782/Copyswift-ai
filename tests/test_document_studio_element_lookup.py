import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioElementLookupTests(unittest.TestCase):

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

    def test_find_element_returns_matching_element(self):
        kernel = EcosystemKernel()

        element = kernel.document_studio.find_element(
            self._document(),
            element_id="image-1",
        )

        self.assertIsNotNone(element)
        self.assertEqual(
            element["id"],
            "image-1",
        )
        self.assertEqual(
            element["type"],
            "image",
        )

    def test_find_element_returns_none_when_not_found(self):
        kernel = EcosystemKernel()

        element = kernel.document_studio.find_element(
            self._document(),
            element_id="missing",
        )

        self.assertIsNone(element)

    def test_find_element_does_not_modify_document(self):
        kernel = EcosystemKernel()

        document = self._document()

        before = repr(document)

        kernel.document_studio.find_element(
            document,
            element_id="text-1",
        )

        self.assertEqual(
            repr(document),
            before,
        )


if __name__ == "__main__":
    unittest.main()
