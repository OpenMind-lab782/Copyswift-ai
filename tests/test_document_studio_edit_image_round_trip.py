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
                                    "text": "Original Heading",
                                    "bbox": (72, 90, 240, 112),
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
                "content": content,
                "fontname": fontname,
                "fontsize": fontsize,
            }
        )

    def insert_image(self, rect, stream=None):
        self.operations.append(
            {
                "type": "image",
                "stream": stream,
                "rect": rect,
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
        return b"%PDF-image-edit-round-trip%"

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


class DocumentStudioEditImageRoundTripTests(unittest.TestCase):

    def test_import_edit_image_export(self):
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

            image = next(
                element
                for element in imported["pages"][0]["elements"]
                if element["type"] == "image"
            )

            edited = kernel.document_studio.edit_image(
                imported,
                element_id=image["id"],
                image_data=b"UPDATED-IMAGE",
            )

            rendered = kernel.document_studio.export_document(
                edited,
                output_name="edited-image.pdf",
            )

        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

        self.assertEqual(
            rendered,
            b"%PDF-image-edit-round-trip%",
        )

        page = FakeFitz.created_pdfs[0].pages[0]

        image_operations = [
            operation
            for operation in page.operations
            if operation["type"] == "image"
        ]

        self.assertEqual(
            len(image_operations),
            1,
        )

        self.assertEqual(
            image_operations[0]["stream"],
            b"UPDATED-IMAGE",
        )

        text_operations = [
            operation
            for operation in page.operations
            if operation["type"] == "text"
        ]

        self.assertEqual(
            len(text_operations),
            1,
        )

        self.assertEqual(
            text_operations[0]["content"],
            "Original Heading",
        )


if __name__ == "__main__":
    unittest.main()
