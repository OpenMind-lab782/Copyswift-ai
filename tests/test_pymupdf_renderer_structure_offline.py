import sys
import types
import unittest

from ecosystem_core.document_renderers.pymupdf_renderer import PyMuPDFRenderer


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
            (
                "text",
                content,
                position,
            )
        )

    def insert_image(self, rect, stream=None):
        self.operations.append(
            (
                "image",
                stream,
                rect.x0,
                rect.y0,
                rect.x1,
                rect.y1,
            )
        )


class FakePDF:
    def __init__(self):
        self.pages = []

    def new_page(self, width, height):
        page = FakePDFPage(width, height)
        self.pages.append(page)
        return page

    def tobytes(self):
        return b"%PDF-structure-test%"

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


class PyMuPDFRendererStructureOfflineTests(unittest.TestCase):

    def test_multiple_pages_and_element_order_are_preserved(self):
        original_fitz = sys.modules.get("fitz")

        fake_module = types.ModuleType("fitz")
        fake_module.open = FakeFitz.open
        fake_module.Rect = FakeFitz.Rect
        sys.modules["fitz"] = fake_module

        FakeFitz.created.clear()

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
                            "content": "Page One",
                            "x": 72,
                            "y": 100,
                            "font_size": 12,
                            "color": 0,
                        },
                        {
                            "id": "image-1",
                            "type": "image",
                            "x": 100,
                            "y": 200,
                            "width": 50,
                            "height": 40,
                            "image_data": b"image-1",
                        },
                    ],
                },
                {
                    "number": 2,
                    "width": 612,
                    "height": 792,
                    "elements": [
                        {
                            "id": "text-2",
                            "type": "text",
                            "content": "Page Two",
                            "x": 80,
                            "y": 110,
                            "font_size": 12,
                            "color": 0,
                        },
                    ],
                },
            ],
        }

        try:
            result = PyMuPDFRenderer().render(
                document,
                output_name="structure.pdf",
            )
        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

        self.assertEqual(
            result,
            b"%PDF-structure-test%",
        )

        pdf = FakeFitz.created[0]

        self.assertEqual(len(pdf.pages), 2)

        self.assertEqual(
            (pdf.pages[0].width, pdf.pages[0].height),
            (595, 842),
        )
        self.assertEqual(
            (pdf.pages[1].width, pdf.pages[1].height),
            (612, 792),
        )

        self.assertEqual(
            pdf.pages[0].operations[0][0],
            "text",
        )
        self.assertEqual(
            pdf.pages[0].operations[0][1],
            "Page One",
        )
        self.assertEqual(
            pdf.pages[0].operations[1][0],
            "image",
        )
        self.assertEqual(
            pdf.pages[0].operations[1][1],
            b"image-1",
        )
        self.assertEqual(
            pdf.pages[1].operations[0][1],
            "Page Two",
        )


if __name__ == "__main__":
    unittest.main()
