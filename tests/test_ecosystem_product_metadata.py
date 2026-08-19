import unittest

from ecosystem_core.kernel import EcosystemKernel


class EcosystemProductMetadataTests(unittest.TestCase):

    def test_products_have_metadata(self):
        kernel = EcosystemKernel()

        copyswift = kernel.products.get("copyswiftai")
        seo_agent = kernel.products.get("seo_agent")
        document_studio = kernel.products.get("document_studio")

        self.assertIsInstance(copyswift, dict)
        self.assertIsInstance(seo_agent, dict)
        self.assertIsInstance(document_studio, dict)

    def test_required_metadata_fields_exist(self):
        kernel = EcosystemKernel()

        for product_name in (
            "copyswiftai",
            "seo_agent",
            "document_studio",
        ):
            product = kernel.products.get(product_name)

            self.assertIn("name", product)
            self.assertIn("type", product)
            self.assertIn("status", product)
            self.assertIn("version", product)

    def test_approved_product_statuses(self):
        kernel = EcosystemKernel()

        self.assertEqual(
            kernel.products.get("copyswiftai")["status"],
            "active",
        )
        self.assertEqual(
            kernel.products.get("seo_agent")["status"],
            "planned",
        )
        self.assertEqual(
            kernel.products.get("document_studio")["status"],
            "planned",
        )


if __name__ == "__main__":
    unittest.main()
