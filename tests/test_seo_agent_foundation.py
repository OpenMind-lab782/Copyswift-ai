import unittest

from ecosystem_core.kernel import EcosystemKernel
from ecosystem_core.seo_agent import SEOAgent


class SEOAgentFoundationTests(unittest.TestCase):

    def test_seo_agent_initializes(self):
        kernel = EcosystemKernel()

        agent = SEOAgent(
            provider=kernel.ai_provider
        )

        self.assertIsNotNone(agent)

    def test_kernel_exposes_seo_agent(self):
        kernel = EcosystemKernel()

        self.assertIsNotNone(kernel.seo_agent)

    def test_kernel_seo_agent_uses_shared_provider(self):
        kernel = EcosystemKernel()

        self.assertIs(
            kernel.seo_agent.provider,
            kernel.ai_provider,
        )

    def test_kernel_registers_seo_agent_service(self):
        kernel = EcosystemKernel()

        self.assertTrue(
            kernel.ai_services.has_service("seo_agent")
        )
        self.assertIs(
            kernel.ai_services.get_service("seo_agent"),
            kernel.seo_agent,
        )

    def test_seo_agent_product_metadata_is_registered(self):
        kernel = EcosystemKernel()

        product = kernel.products.get("seo_agent")

        self.assertIsInstance(product, dict)
        self.assertEqual(product["status"], "planned")

    def test_seo_agent_has_stable_result_contract(self):
        kernel = EcosystemKernel()

        agent = SEOAgent(
            provider=kernel.ai_provider
        )

        result = agent.analyze(
            keyword="ai copywriting",
            content="AI copywriting helps businesses create marketing content.",
        )

        self.assertIsInstance(result, dict)
        self.assertIn("keyword", result)
        self.assertIn("score", result)
        self.assertIn("recommendations", result)


if __name__ == "__main__":
    unittest.main()
