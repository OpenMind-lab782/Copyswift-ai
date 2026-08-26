import unittest

from ecosystem_core.kernel import EcosystemKernel


class EcosystemKernelProductTests(unittest.TestCase):

    def test_kernel_exposes_product_registry(self):
        kernel = EcosystemKernel()

        self.assertIsNotNone(kernel.products)

    def test_core_products_are_registered(self):
        kernel = EcosystemKernel()

        self.assertIn("copyswiftai", kernel.products.list_products())
        self.assertIn("seo_agent", kernel.products.list_products())
        self.assertIn("document_studio", kernel.products.list_products())


if __name__ == "__main__":
    unittest.main()
