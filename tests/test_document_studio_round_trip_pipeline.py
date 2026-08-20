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
        if mode != "dict":
            raise AssertionError(
                f"Unexpected extraction mode: {mode}"
            )

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
                    "image": b"ORIGINAL-IMAGE-BYTES",
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
        return b"%PDF-round-trip-pipeline%"

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


class DocumentStudioRoundTripPipelineTests(unittest.TestCase):

    def test_import_edit_export_round_trip(self):
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

            imported = (
                kernel.document_studio.import_binary_document(
                    b"fake-pdf",
                    file_name="sample.pdf",
                )
            )

            self.assertEqual(
                imported["page_count"],
                1,
            )

            elements = imported["pages"][0]["elements"]

            text_element = next(
                element
                for element in elements
                if element["type"] == "text"
            )

            image_element = next(
                element
                for element in elements
                if element["type"] == "image"
            )

            self.assertEqual(
                text_element["content"],
                "Original Heading",
            )
            self.assertEqual(
                text_element["font"],
                "Helvetica-Bold",
            )
            self.assertEqual(
                text_element["font_size"],
                16,
            )
            self.assertEqual(
                image_element["image_data"],
                b"ORIGINAL-IMAGE-BYTES",
            )

            edited = kernel.document_studio.edit_text(
                imported,
                element_id=text_element["id"],
                new_content="Updated Heading",
            )

            output = kernel.document_studio.export_document(
                edited,
                output_name="edited.pdf",
            )

        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

        self.assertEqual(
            output,
            b"%PDF-round-trip-pipeline%",
        )

        pdf = FakeFitz.created_pdfs[0]
        page = pdf.pages[0]

        self.assertEqual(
            len(page.operations),
            2,
        )

        text_operation = page.operations[0]
        image_operation = page.operations[1]

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
            image_operation["stream"],
            b"ORIGINAL-IMAGE-BYTES",
        )

    def test_round_trip_does_not_modify_imported_source_document(self):
        original_fitz = sys.modules.get("fitz")

        fake_module = types.ModuleType("fitz")
        fake_module.open = FakeFitz.open
        fake_module.Rect = FakeFitz.Rect
        sys.modules["fitz"] = fake_module

        kernel = EcosystemKernel()

        try:
            kernel.register_document_adapter(
                "pdf",
                PyMuPDFAdapter(),
            )

            kernel.document_renderer.engine = PyMuPDFRenderer()

            imported = (
                kernel.document_studio.import_binary_document(
                    b"fake-pdf",
                    file_name="sample.pdf",
                )
            )

            original_content = (
                imported["pages"][0]["elements"][0]["content"]
            )

            edited = kernel.document_studio.edit_text(
                imported,
                element_id="page-1-block-1-line-1-span-1",
                new_content="Updated Heading",
            )

            kernel.document_studio.export_document(
                edited,
                output_name="edited.pdf",
            )

        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

        self.assertEqual(
            imported["pages"][0]["elements"][0]["content"],
            original_content,
        )


if __name__ == "__main__":
    unittest.main()
