import unittest

from ecosystem_core.kernel import EcosystemKernel


class EcosystemKernelTests(unittest.TestCase):

    def test_kernel_initializes(self):
        kernel = EcosystemKernel()

        self.assertIsNotNone(kernel)

    def test_kernel_exposes_ai_provider(self):
        kernel = EcosystemKernel()

        self.assertIsNotNone(kernel.ai_provider)

    def test_kernel_exposes_payment_engine(self):
        kernel = EcosystemKernel()

        self.assertIsNotNone(kernel.payment_engine)

    def test_kernel_exposes_unified_assistant(self):
        kernel = EcosystemKernel()

        self.assertIsNotNone(kernel.assistant)

    def test_kernel_registers_existing_ai_services(self):
        kernel = EcosystemKernel()

        services = kernel.ai_services.list_services()

        self.assertIn("market_brain", services)
        self.assertIn("market_strategist", services)
        self.assertIn("sales_manager", services)


if __name__ == "__main__":
    unittest.main()
