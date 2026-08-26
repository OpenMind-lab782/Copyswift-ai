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
                    "type": 1,
                    "bbox": (100, 200, 300, 350),
                    "width": 200,
                    "height": 150,
                    "ext": "png",
                    "xres": 96,
                    "yres": 96,
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


class PyMuPDFImageExtractionTests(unittest.TestCase):

    def test_image_block_becomes_positioned_image_element(self):
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

        elements = result["pages"][0]["elements"]

        image_elements = [
            element
            for element in elements
            if element.get("type") == "image"
        ]

        self.assertEqual(len(image_elements), 1)

        image = image_elements[0]

        self.assertEqual(image["x"], 100)
        self.assertEqual(image["y"], 200)
        self.assertEqual(image["width"], 200)
        self.assertEqual(image["height"], 150)

    def test_image_element_has_stable_id_and_format_metadata(self):
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

        self.assertTrue(
            str(image.get("id", "")).strip()
        )
        self.assertEqual(
            image["image_format"],
            "png",
        )


if __name__ == "__main__":
    unittest.main()
