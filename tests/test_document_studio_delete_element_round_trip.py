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
                                    "text": "Keep This Text",
                                    "bbox": (72, 90, 180, 110),
                                    "font": "Helvetica",
                                    "size": 12,
                                    "flags": 0,
                                    "color": 0,
                                }
                            ]
                        }
                    ],
                },
                {
                    "type": 0,
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Delete This Text",
                                    "bbox": (72, 130, 190, 150),
                                    "font": "Helvetica",
                                    "size": 12,
                                    "flags": 0,
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
                    "image": b"IMAGE-BYTES",
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
        return b"%PDF-delete-round-trip%"

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


class DocumentStudioDeleteElementRoundTripTests(unittest.TestCase):

    def test_delete_then_export_removes_only_target(self):
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

            delete_target = next(
                element
                for element in imported["pages"][0]["elements"]
                if element.get("content") == "Delete This Text"
            )

            edited = kernel.document_studio.delete_element(
                imported,
                element_id=delete_target["id"],
            )

            rendered = kernel.document_studio.export_document(
                edited,
                output_name="deleted.pdf",
            )

        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

        self.assertEqual(
            rendered,
            b"%PDF-delete-round-trip%",
        )

        page = FakeFitz.created_pdfs[0].pages[0]

        contents = [
            operation["content"]
            for operation in page.text_operations
        ]

        self.assertIn(
            "Keep This Text",
            contents,
        )
        self.assertNotIn(
            "Delete This Text",
            contents,
        )

        self.assertEqual(
            len(page.image_operations),
            1,
        )
        self.assertEqual(
            page.image_operations[0]["stream"],
            b"IMAGE-BYTES",
        )


if __name__ == "__main__":
    unittest.main()
