import unittest

from ecosystem_core.kernel import EcosystemKernel


class DocumentEngineRegistrationAPITests(unittest.TestCase):

    def test_kernel_can_register_pdf_engine(self):
        kernel = EcosystemKernel()

        class FakePDFEngine:
            def parse(self, data, file_name):
                return {
                    "name": file_name,
                    "pages": [],
                }

        kernel.register_document_adapter(
            "pdf",
            FakePDFEngine(),
        )

        self.assertIs(
            kernel.document_parser.adapters["pdf"].__class__,
            FakePDFEngine,
        )

    def test_registered_pdf_engine_is_used_by_parser(self):
        kernel = EcosystemKernel()

        class FakePDFEngine:
            def parse(self, data, file_name):
                return {
                    "name": file_name,
                    "pages": [],
                }

        kernel.register_document_adapter(
            "pdf",
            FakePDFEngine(),
        )

        result = kernel.document_parser.parse(
            b"fake-pdf",
            file_name="sample.pdf",
        )

        self.assertEqual(
            result["name"],
            "sample.pdf",
        )

    def test_registration_rejects_unsupported_format(self):
        kernel = EcosystemKernel()

        class FakeAdapter:
            def parse(self, data, file_name):
                return {}

        with self.assertRaises(ValueError):
            kernel.register_document_adapter(
                "xyz",
                FakeAdapter(),
            )


if __name__ == "__main__":
    unittest.main()
