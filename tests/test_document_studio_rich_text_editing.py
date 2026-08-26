import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentStudioRichTextEditingTests(unittest.TestCase):

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
                            "content": "Original Heading",
                            "x": 72,
                            "y": 90,
                            "width": 168,
                            "height": 22,
                            "font": "Helvetica-Bold",
                            "font_size": 16,
                            "flags": 20,
                            "color": 0,
                        },
                        {
                            "id": "image-1",
                            "type": "image",
                            "x": 100,
                            "y": 200,
                            "width": 200,
                            "height": 150,
                            "image_format": "png",
                            "xres": 96,
                            "yres": 96,
                        },
                    ],
                }
            ],
        }

    def test_edit_text_style_updates_supported_style_metadata(self):
        kernel = EcosystemKernel()
        result = kernel.document_studio.edit_text_style(
            self._document(),
            element_id="text-1",
            font="Helvetica",
            font_size=20,
            color="#FF0000",
        )
        element = result["pages"][0]["elements"][0]
        self.assertEqual(element["font"], "Helvetica")
        self.assertEqual(element["font_size"], 20)
        self.assertEqual(element["color"], "#FF0000")

    def test_edit_text_style_preserves_content_and_geometry(self):
        kernel = EcosystemKernel()
        original = self._document()
        result = kernel.document_studio.edit_text_style(
            original,
            element_id="text-1",
            font_size=20,
        )
        updated = result["pages"][0]["elements"][0]
        source = original["pages"][0]["elements"][0]
        self.assertEqual(updated["content"], source["content"])
        self.assertEqual(updated["x"], source["x"])
        self.assertEqual(updated["y"], source["y"])
        self.assertEqual(updated["width"], source["width"])
        self.assertEqual(updated["height"], source["height"])

    def test_edit_text_style_preserves_omitted_style_values(self):
        kernel = EcosystemKernel()
        result = kernel.document_studio.edit_text_style(
            self._document(),
            element_id="text-1",
            font_size=20,
        )
        element = result["pages"][0]["elements"][0]
        self.assertEqual(element["font"], "Helvetica-Bold")
        self.assertEqual(element["font_size"], 20)
        self.assertEqual(element["color"], 0)
        self.assertEqual(element["flags"], 20)

    def test_edit_text_style_does_not_modify_source_document(self):
        kernel = EcosystemKernel()
        original = self._document()
        kernel.document_studio.edit_text_style(
            original,
            element_id="text-1",
            font="Helvetica",
            font_size=20,
            color="#FF0000",
        )
        element = original["pages"][0]["elements"][0]
        self.assertEqual(element["font"], "Helvetica-Bold")
        self.assertEqual(element["font_size"], 16)
        self.assertEqual(element["color"], 0)

    def test_edit_text_style_rejects_image_elements(self):
        kernel = EcosystemKernel()
        with self.assertRaises(ValueError):
            kernel.document_studio.edit_text_style(
                self._document(),
                element_id="image-1",
                font_size=20,
            )

    def test_edit_text_style_rejects_missing_elements(self):
        kernel = EcosystemKernel()
        with self.assertRaises(KeyError):
            kernel.document_studio.edit_text_style(
                self._document(),
                element_id="missing-text",
                font_size=20,
            )

    def test_edit_text_preserves_style_metadata(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.edit_text(
            self._document(),
            element_id="text-1",
            new_content="Updated Heading",
        )

        element = result["pages"][0]["elements"][0]

        self.assertEqual(
            element["content"],
            "Updated Heading",
        )
        self.assertEqual(
            element["font"],
            "Helvetica-Bold",
        )
        self.assertEqual(
            element["font_size"],
            16,
        )
        self.assertEqual(
            element["flags"],
            20,
        )
        self.assertEqual(
            element["color"],
            0,
        )

    def test_edit_text_preserves_geometry(self):
        kernel = EcosystemKernel()

        original = self._document()

        result = kernel.document_studio.edit_text(
            original,
            element_id="text-1",
            new_content="Updated Heading",
        )

        updated = result["pages"][0]["elements"][0]
        source = original["pages"][0]["elements"][0]

        self.assertEqual(updated["x"], source["x"])
        self.assertEqual(updated["y"], source["y"])
        self.assertEqual(updated["width"], source["width"])
        self.assertEqual(updated["height"], source["height"])

    def test_edit_text_does_not_modify_image_elements(self):
        kernel = EcosystemKernel()

        result = kernel.document_studio.edit_text(
            self._document(),
            element_id="text-1",
            new_content="Updated Heading",
        )

        image = result["pages"][0]["elements"][1]

        self.assertEqual(image["type"], "image")
        self.assertEqual(image["x"], 100)
        self.assertEqual(image["y"], 200)
        self.assertEqual(image["width"], 200)
        self.assertEqual(image["height"], 150)
        self.assertEqual(image["image_format"], "png")


if __name__ == "__main__":
    unittest.main()
