import sys
import types
import unittest

from ecosystem_core.document_renderers.pymupdf_renderer import PyMuPDFRenderer


class FakePDFPage:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.inserted_images = []

    def insert_image(self, rect, stream=None):
        self.inserted_images.append(
            {
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
        return b"%PDF-image-test%"

    def close(self):
        pass


class FakeFitz:

    created = []

    @staticmethod
    def open():
        pdf = FakePDF()
        FakeFitz.created.append(pdf)
        return pdf

    class Rect:
        def __init__(self, x0, y0, x1, y1):
            self.x0 = x0
            self.y0 = y0
            self.x1 = x1
            self.y1 = y1


class PyMuPDFRendererImageOfflineTests(unittest.TestCase):

    def test_image_element_is_rendered_with_position_and_size(self):
        original_fitz = sys.modules.get("fitz")

        fake_module = types.ModuleType("fitz")
        fake_module.open = FakeFitz.open
        fake_module.Rect = FakeFitz.Rect
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
                                    "id": "image-1",
                                    "type": "image",
                                    "x": 100,
                                    "y": 200,
                                    "width": 200,
                                    "height": 150,
                                    "image_data": b"fake-image-bytes",
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
            b"%PDF-image-test%",
        )

        page = FakeFitz.created[0].pages[0]

        self.assertEqual(
            len(page.inserted_images),
            1,
        )

        image = page.inserted_images[0]

        self.assertEqual(
            image["rect"].x0,
            100.0,
        )
        self.assertEqual(
            image["rect"].y0,
            200.0,
        )
        self.assertEqual(
            image["rect"].x1,
            300.0,
        )
        self.assertEqual(
            image["rect"].y1,
            350.0,
        )
        self.assertEqual(
            image["stream"],
            b"fake-image-bytes",
        )


if __name__ == "__main__":
    unittest.main()
