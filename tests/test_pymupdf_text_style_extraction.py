import sys
import types
import unittest

from ecosystem_core.document_adapters.pymupdf_adapter import PyMuPDFAdapter


class FakePage:

    class Rect:
        width = 595
        height = 842

    rect = Rect()

    def get_text(self, mode):
        return {
            "blocks": [
                {
                    "type": 0,
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Styled Heading",
                                    "bbox": (72, 90, 240, 112),
                                    "font": "Helvetica-Bold",
                                    "size": 16,
                                    "flags": 20,
                                    "color": 0,
                                }
                            ]
                        }
                    ],
                }
            ]
        }


class FakeDocument:
    def __iter__(self):
        return iter([FakePage()])

    def close(self):
        pass


class FakeFitz:
    @staticmethod
    def open(stream, filetype):
        return FakeDocument()


class PyMuPDFTextStyleExtractionTests(unittest.TestCase):

    def test_text_style_metadata_is_preserved(self):
        original_fitz = sys.modules.get("fitz")

        fake_module = types.ModuleType("fitz")
        fake_module.open = FakeFitz.open
        sys.modules["fitz"] = fake_module

        try:
            result = PyMuPDFAdapter().parse(
                b"fake-pdf",
                file_name="styled.pdf",
            )
        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

        element = result["pages"][0]["elements"][0]

        self.assertEqual(
            element["content"],
            "Styled Heading",
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


if __name__ == "__main__":
    unittest.main()
