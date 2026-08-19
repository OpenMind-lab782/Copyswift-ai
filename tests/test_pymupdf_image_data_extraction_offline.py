import sys
import types
import unittest

from ecosystem_core.document_adapters.pymupdf_adapter import PyMuPDFAdapter


class FakeRect:
    width = 595
    height = 842


class FakePage:
    rect = FakeRect()

    def get_text(self, mode):
        return {
            "blocks": [
                {
                    "type": 1,
                    "bbox": (100, 200, 300, 350),
                    "ext": "png",
                    "xres": 96,
                    "yres": 96,
                    "image": b"ORIGINAL-IMAGE-BYTES",
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


class PyMuPDFImageDataExtractionOfflineTests(unittest.TestCase):

    def test_image_binary_data_is_preserved(self):
        original_fitz = sys.modules.get("fitz")

        fake_module = types.ModuleType("fitz")
        fake_module.open = FakeFitz.open
        sys.modules["fitz"] = fake_module

        try:
            result = PyMuPDFAdapter().parse(
                b"fake-pdf",
                file_name="image.pdf",
            )
        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

        image = result["pages"][0]["elements"][0]

        self.assertEqual(
            image["type"],
            "image",
        )
        self.assertEqual(
            image["image_data"],
            b"ORIGINAL-IMAGE-BYTES",
        )


if __name__ == "__main__":
    unittest.main()
