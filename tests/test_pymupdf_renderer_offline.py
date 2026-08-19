import sys
import types
import unittest

from ecosystem_core.document_renderers.pymupdf_renderer import PyMuPDFRenderer


class FakePDFPage:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.inserted_text = []

    def insert_text(
        self,
        position,
        content,
        fontname,
        fontsize,
        color,
    ):
        self.inserted_text.append(
            {
                "position": position,
                "content": content,
                "fontname": fontname,
                "fontsize": fontsize,
                "color": color,
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
        return b"%PDF-offline-test%"

    def close(self):
        pass


class FakeFitz:

    created = []

    @staticmethod
    def open():
        pdf = FakePDF()
        FakeFitz.created.append(pdf)
        return pdf


class PyMuPDFRendererOfflineTests(unittest.TestCase):

    def test_text_rendering_logic_without_native_engine(self):
        original_fitz = sys.modules.get("fitz")

        fake_module = types.ModuleType("fitz")
        fake_module.open = FakeFitz.open
        sys.modules["fitz"] = fake_module

        FakeFitz.created.clear()

        try:
            renderer = PyMuPDFRenderer()

            result = renderer.render(
                {
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
                                    "content": "Hello World",
                                    "x": 72,
                                    "y": 100,
                                    "font": "Helvetica-Bold",
                                    "font_size": 16,
                                    "color": 0,
                                }
                            ],
                        }
                    ],
                },
                output_name="edited.pdf",
            )
        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

        self.assertEqual(
            result,
            b"%PDF-offline-test%",
        )

        pdf = FakeFitz.created[0]

        self.assertEqual(
            len(pdf.pages),
            1,
        )

        page = pdf.pages[0]

        self.assertEqual(
            page.width,
            595,
        )
        self.assertEqual(
            page.height,
            842,
        )

        self.assertEqual(
            len(page.inserted_text),
            1,
        )

        inserted = page.inserted_text[0]

        self.assertEqual(
            inserted["position"],
            (72.0, 100.0),
        )
        self.assertEqual(
            inserted["content"],
            "Hello World",
        )
        self.assertEqual(
            inserted["fontname"],
            "Helvetica-Bold",
        )
        self.assertEqual(
            inserted["fontsize"],
            16.0,
        )

    def test_color_conversion(self):
        self.assertEqual(
            PyMuPDFRenderer._color_to_rgb(0xFF0000),
            (1.0, 0.0, 0.0),
        )
        self.assertEqual(
            PyMuPDFRenderer._color_to_rgb(0x00FF00),
            (0.0, 1.0, 0.0),
        )
        self.assertEqual(
            PyMuPDFRenderer._color_to_rgb(0x0000FF),
            (0.0, 0.0, 1.0),
        )


if __name__ == "__main__":
    unittest.main()
