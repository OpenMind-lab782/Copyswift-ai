import sys
import types
import unittest

from ecosystem_core.document_renderers.pymupdf_renderer import PyMuPDFRenderer
from ecosystem_core.kernel import EcosystemKernel


class FakePDFPage:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.operations = []

    def insert_text(
        self,
        position,
        content,
        fontname,
        fontsize,
        color,
    ):
        self.operations.append(
            {
                "type": "text",
                "position": position,
                "content": content,
                "fontname": fontname,
                "fontsize": fontsize,
                "color": color,
            }
        )

    def insert_image(self, rect, stream=None):
        self.operations.append(
            {
                "type": "image",
                "rect": rect,
                "stream": stream,
            }
        )


class FakePDF:
    def __init__(self):
        self.pages = []

    def new_page(self, width, height):
        page = FakePDFPage(width, height)
        self.pages.append(page)
        return page

    def tobytes(self):
        return b"%PDF-edit-render-test%"

    def close(self):
        pass


class FakeFitz:
    created = []

    class Rect:
        def __init__(self, x0, y0, x1, y1):
            self.x0 = x0
            self.y0 = y0
            self.x1 = x1
            self.y1 = y1

    @staticmethod
    def open():
        pdf = FakePDF()
        FakeFitz.created.append(pdf)
        return pdf


class DocumentStudioEditRenderOfflineTests(unittest.TestCase):

    def test_edit_then_render_preserves_edited_text_and_image(self):
        original_fitz = sys.modules.get("fitz")

        fake_module = types.ModuleType("fitz")
        fake_module.open = FakeFitz.open
        fake_module.Rect = FakeFitz.Rect
        sys.modules["fitz"] = fake_module

        FakeFitz.created.clear()

        kernel = EcosystemKernel()
        original_image = b"ORIGINAL-IMAGE-BYTES"

        document = {
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
                            "image_data": original_image,
                        },
                    ],
                }
            ],
        }

        try:
            edited = kernel.document_studio.edit_text(
                document,
                element_id="text-1",
                new_content="Updated Heading",
            )

            rendered = PyMuPDFRenderer().render(
                edited,
                output_name="edited.pdf",
            )
        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

        self.assertEqual(
            rendered,
            b"%PDF-edit-render-test%",
        )

        pdf = FakeFitz.created[0]
        page = pdf.pages[0]

        self.assertEqual(len(page.operations), 2)

        text_operation = page.operations[0]
        image_operation = page.operations[1]

        self.assertEqual(
            text_operation["type"],
            "text",
        )
        self.assertEqual(
            text_operation["content"],
            "Updated Heading",
        )
        self.assertEqual(
            text_operation["fontname"],
            "Helvetica-Bold",
        )
        self.assertEqual(
            text_operation["fontsize"],
            16.0,
        )

        self.assertEqual(
            image_operation["type"],
            "image",
        )
        self.assertEqual(
            image_operation["stream"],
            original_image,
        )


if __name__ == "__main__":
    unittest.main()
