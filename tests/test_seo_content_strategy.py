import unittest

from ecosystem_core.kernel import EcosystemKernel


class SEOContentStrategyTests(unittest.TestCase):

    def test_content_strategy_returns_expected_structure(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.build_content_strategy(
            seed_keyword="ai copywriting"
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["seed_keyword"], "ai copywriting")
        self.assertIn("pillars", result)
        self.assertIn("content_plan", result)
        self.assertIn("recommendations", result)

    def test_content_strategy_creates_content_pillars(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.build_content_strategy(
            seed_keyword="ai copywriting"
        )

        self.assertGreaterEqual(
            len(result["pillars"]),
            3,
        )

    def test_content_plan_has_expected_fields(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.build_content_strategy(
            seed_keyword="ai copywriting"
        )

        self.assertGreaterEqual(
            len(result["content_plan"]),
            5,
        )

        for item in result["content_plan"]:
            self.assertIn("title", item)
            self.assertIn("keyword", item)
            self.assertIn("intent", item)
            self.assertIn("content_type", item)

    def test_content_strategy_is_deterministic(self):
        kernel = EcosystemKernel()

        first = kernel.seo_agent.build_content_strategy(
            seed_keyword="ai copywriting"
        )
        second = kernel.seo_agent.build_content_strategy(
            seed_keyword="ai copywriting"
        )

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
