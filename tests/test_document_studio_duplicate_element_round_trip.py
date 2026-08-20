import sys
import types
import unittest

from ecosystem_core.document_adapters.pymupdf_adapter import PyMuPDFAdapter
from ecosystem_core.document_renderers.pymupdf_renderer import PyMuPDFRenderer
from ecosystem_core.kernel import EcosystemKernel


class FakeRect:
    width = 595
    height = 842


class FakePage:
    rect = FakeRect()

    def get_text(self, mode):
        return {
            "blocks": [
                {
                    "type": 0,
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Original Text",
                                    "bbox": (72, 90, 180, 110),
                                    "font": "Helvetica-Bold",
                                    "size": 16,
                                    "flags": 20,
                                    "color": 0,
                                }
                            ]
                        }
                    ],
                },
                {
                    "type": 1,
                    "bbox": (100, 200, 300, 350),
                    "ext": "png",
                    "xres": 96,
                    "yres": 96,
                    "image": b"ORIGINAL-IMAGE",
                },
            ]
        }


class FakeDocument:
    def __iter__(self):
        return iter([FakePage()])

    def close(self):
        pass


class FakePDFPage:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.text_operations = []
        self.image_operations = []

    def insert_text(
        self,
        position,
        content,
        fontname,
        fontsize,
        color,
    ):
        self.text_operations.append(
            {
                "position": position,
                "content": content,
                "fontname": fontname,
                "fontsize": fontsize,
            }
        )

    def insert_image(self, rect, stream=None):
        self.image_operations.append(
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
        return b"%PDF-duplicate-round-trip%"

    def close(self):
        pass


class FakeFitz:
    created_pdfs = []

    class Rect:
        def __init__(self, x0, y0, x1, y1):
            self.x0 = x0
            self.y0 = y0
            self.x1 = x1
            self.y1 = y1

    @staticmethod
    def open(*args, **kwargs):
        if kwargs.get("stream") is not None:
            return FakeDocument()

        pdf = FakePDF()
        FakeFitz.created_pdfs.append(pdf)
        return pdf


class DocumentStudioDuplicateElementRoundTripTests(unittest.TestCase):

    def test_duplicate_text_and_image_reach_renderer(self):
        original_fitz = sys.modules.get("fitz")

        fake_module = types.ModuleType("fitz")
        fake_module.open = FakeFitz.open
        fake_module.Rect = FakeFitz.Rect
        sys.modules["fitz"] = fake_module

        FakeFitz.created_pdfs.clear()

        kernel = EcosystemKernel()

        try:
            kernel.register_document_adapter(
                "pdf",
                PyMuPDFAdapter(),
            )
            kernel.document_renderer.engine = PyMuPDFRenderer()

            imported = kernel.document_studio.import_binary_document(
                b"fake-pdf",
                file_name="sample.pdf",
            )

            text = next(
                element
                for element in imported["pages"][0]["elements"]
                if element["type"] == "text"
            )

            image = next(
                element
                for element in imported["pages"][0]["elements"]
                if element["type"] == "image"
            )

            duplicated = kernel.document_studio.duplicate_element(
                imported,
                element_id=text["id"],
                new_element_id="text-copy",
                x=200,
                y=300,
            )

            duplicated = kernel.document_studio.duplicate_element(
                duplicated,
                element_id=image["id"],
                new_element_id="image-copy",
                x=250,
                y=350,
            )

            rendered = kernel.document_studio.export_document(
                duplicated,
                output_name="duplicated.pdf",
            )

        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

        self.assertEqual(
            rendered,
            b"%PDF-duplicate-round-trip%",
        )

        page = FakeFitz.created_pdfs[0].pages[0]

        self.assertEqual(
            len(page.text_operations),
            2,
        )
        self.assertEqual(
            len(page.image_operations),
            2,
        )

        text_positions = [
            operation["position"]
            for operation in page.text_operations
            if operation["content"] == "Original Text"
        ]

        self.assertEqual(
            text_positions,
            [
                (72.0, 90.0),
                (200.0, 300.0),
            ],
        )

        image_streams = [
            operation["stream"]
            for operation in page.image_operations
        ]

        self.assertEqual(
            image_streams,
            [
                b"ORIGINAL-IMAGE",
                b"ORIGINAL-IMAGE",
            ],
        )


if __name__ == "__main__":
    unittest.main()
