import sys
import types
import unittest

from ecosystem_core.kernel import EcosystemKernel
from ecosystem_core.document_adapters.pymupdf_adapter import PyMuPDFAdapter


class FakeRect:
    width = 595
    height = 842


class FakePage:
    rect = FakeRect()

    def get_text(self, mode):
        self._assert_mode(mode)

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
                },
            ]
        }

    @staticmethod
    def _assert_mode(mode):
        if mode != "dict":
            raise AssertionError(
                f"Unexpected extraction mode: {mode}"
            )


class FakeDocument:
    def __iter__(self):
        return iter([FakePage()])

    def close(self):
        pass


class FakeFitz:
    @staticmethod
    def open(stream, filetype):
        return FakeDocument()


class PyMuPDFFullPipelineOfflineTests(unittest.TestCase):

    def test_kernel_pipeline_produces_rich_canonical_document(self):
        original_fitz = sys.modules.get("fitz")

        fake_module = types.ModuleType("fitz")
        fake_module.open = FakeFitz.open
        sys.modules["fitz"] = fake_module

        try:
            kernel = EcosystemKernel()

            kernel.register_document_adapter(
                "pdf",
                PyMuPDFAdapter(),
            )

            parsed = kernel.document_parser.parse(
                b"fake-pdf",
                file_name="sample.pdf",
            )

            canonical = kernel.document_importer.normalize(
                parsed
            )
        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

        self.assertEqual(
            canonical["name"],
            "sample.pdf",
        )
        self.assertEqual(
            canonical["page_count"],
            1,
        )

        elements = canonical["pages"][0]["elements"]

        self.assertEqual(
            len(elements),
            2,
        )

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
            "CopySwiftAI Document Studio",
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
            image_element["image_format"],
            "png",
        )
        self.assertEqual(
            image_element["x"],
            100,
        )
        self.assertEqual(
            image_element["height"],
            150,
        )

    def test_document_studio_can_inspect_pipeline_output(self):
        original_fitz = sys.modules.get("fitz")

        fake_module = types.ModuleType("fitz")
        fake_module.open = FakeFitz.open
        sys.modules["fitz"] = fake_module

        try:
            kernel = EcosystemKernel()

            kernel.register_document_adapter(
                "pdf",
                PyMuPDFAdapter(),
            )

            parsed = kernel.document_parser.parse(
                b"fake-pdf",
                file_name="sample.pdf",
            )

            canonical = kernel.document_importer.normalize(
                parsed
            )

            inspected = kernel.document_studio.inspect_document(
                canonical
            )
        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

        self.assertEqual(
            inspected["name"],
            "sample.pdf",
        )
        self.assertEqual(
            inspected["page_count"],
            1,
        )
        self.assertTrue(
            inspected["structure"]["has_text"]
        )
        self.assertTrue(
            inspected["structure"]["has_positioned_elements"]
        )
        self.assertIn(
            "image",
            inspected["structure"]["element_types"],
        )


if __name__ == "__main__":
    unittest.main()
