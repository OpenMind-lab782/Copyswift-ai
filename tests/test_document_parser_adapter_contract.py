import unittest

from ecosystem_core.document_parser import DocumentParser


class FakePDFAdapter:

    def parse(self, data, file_name):
        return {
            "name": file_name,
            "page_count": 1,
            "pages": [],
            "metadata": {
                "source_format": "pdf",
                "adapter": "fake",
            },
        }


class DocumentParserAdapterContractTests(unittest.TestCase):

    def test_pdf_adapter_is_used(self):
        adapter = FakePDFAdapter()
        parser = DocumentParser(
            adapters={"pdf": adapter}
        )

        result = parser.parse(
            b"fake-pdf-data",
            file_name="sample.pdf",
        )

        self.assertEqual(result["name"], "sample.pdf")
        self.assertEqual(
            result["metadata"]["source_format"],
            "pdf",
        )
        self.assertEqual(
            result["metadata"]["adapter"],
            "fake",
        )

    def test_adapter_receives_original_binary_data(self):
        captured = {}

        class CapturingAdapter:

            def parse(self, data, file_name):
                captured["data"] = data
                captured["file_name"] = file_name

                return {"ok": True}

        parser = DocumentParser(
            adapters={"pdf": CapturingAdapter()}
        )

        payload = b"original-binary-payload"

        result = parser.parse(
            payload,
            file_name="document.pdf",
        )

        self.assertEqual(result, {"ok": True})
        self.assertIs(captured["data"], payload)
        self.assertEqual(
            captured["file_name"],
            "document.pdf",
        )

    def test_missing_supported_adapter_fails_clearly(self):
        parser = DocumentParser()

        with self.assertRaises(RuntimeError):
            parser.parse(
                b"sample",
                file_name="sample.pdf",
            )


if __name__ == "__main__":
    unittest.main()
