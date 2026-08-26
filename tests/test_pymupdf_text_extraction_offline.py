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
        assert mode == "dict"

        return {
            "blocks": [
                {
                    "type": 0,
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "CopySwiftAI Document Studio",
                                    "bbox": (72, 90, 260, 105),
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


class PyMuPDFOfflineTextExtractionTests(unittest.TestCase):

    def test_real_extraction_logic_without_native_engine(self):
        original_fitz = sys.modules.get("fitz")
        sys.modules["fitz"] = types.ModuleType("fitz")
        sys.modules["fitz"].open = FakeFitz.open

        try:
            adapter = PyMuPDFAdapter()

            result = adapter.parse(
                b"fake-pdf",
                file_name="sample.pdf",
            )
        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

        self.assertEqual(
            result["name"],
            "sample.pdf",
        )

        elements = result["pages"][0]["elements"]

        self.assertEqual(
            len(elements),
            1,
        )

        element = elements[0]

        self.assertEqual(
            element["type"],
            "text",
        )
        self.assertEqual(
            element["content"],
            "CopySwiftAI Document Studio",
        )
        self.assertEqual(
            element["x"],
            72,
        )
        self.assertEqual(
            element["y"],
            90,
        )
        self.assertEqual(
            element["width"],
            188,
        )
        self.assertEqual(
            element["height"],
            15,
        )
        self.assertTrue(
            element["id"].startswith("page-1-block-1-line-1-span-1")
        )


if __name__ == "__main__":
    unittest.main()
