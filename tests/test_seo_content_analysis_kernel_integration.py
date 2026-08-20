import unittest

from ecosystem_core.kernel import EcosystemKernel


class SEOContentAnalysisKernelIntegrationTests(unittest.TestCase):

    def test_kernel_service_points_to_same_seo_agent(self):
        kernel = EcosystemKernel()

        service = kernel.ai_services.get_service("seo_agent")

        self.assertIs(
            service,
            kernel.seo_agent,
        )

    def test_kernel_seo_agent_content_analysis_is_available(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_content(
            keyword="seo",
            content=(
                "SEO helps businesses improve visibility. "
                "SEO can support stronger discovery."
            ),
        )

        self.assertEqual(
            result["keyword"],
            "seo",
        )
        self.assertEqual(
            result["keyword_occurrences"],
            2,
        )

    def test_kernel_uses_shared_provider(self):
        kernel = EcosystemKernel()

        self.assertIs(
            kernel.seo_agent.provider,
            kernel.ai_provider,
        )


if __name__ == "__main__":
    unittest.main()
