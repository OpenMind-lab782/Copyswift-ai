import unittest

from ecosystem_core.document_adapters.pymupdf_adapter import PyMuPDFAdapter


class PyMuPDFAdapterTests(unittest.TestCase):

    def test_adapter_initializes(self):
        adapter = PyMuPDFAdapter()

        self.assertIsNotNone(adapter)

    def test_adapter_exposes_parse_method(self):
        adapter = PyMuPDFAdapter()

        self.assertTrue(
            callable(adapter.parse)
        )

    def test_adapter_reports_engine_unavailable_cleanly(self):
        adapter = PyMuPDFAdapter()

        with self.assertRaises(RuntimeError) as context:
            adapter.parse(
                b"not-a-real-pdf",
                file_name="sample.pdf",
            )

        self.assertIn(
            "PyMuPDF",
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()
