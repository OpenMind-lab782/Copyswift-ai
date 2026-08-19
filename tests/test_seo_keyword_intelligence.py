import unittest

from ecosystem_core.kernel import EcosystemKernel


class SEOKeywordIntelligenceTests(unittest.TestCase):

    def test_keyword_analysis_returns_expected_structure(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_keywords(
            seed_keyword="ai copywriting"
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["seed_keyword"], "ai copywriting")
        self.assertIn("keywords", result)
        self.assertIn("clusters", result)
        self.assertIn("recommendations", result)

    def test_keyword_analysis_returns_multiple_opportunities(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_keywords(
            seed_keyword="ai copywriting"
        )

        self.assertGreaterEqual(
            len(result["keywords"]),
            5,
        )

    def test_keyword_results_have_expected_fields(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_keywords(
            seed_keyword="ai copywriting"
        )

        for keyword in result["keywords"]:
            self.assertIn("keyword", keyword)
            self.assertIn("intent", keyword)
            self.assertIn("opportunity", keyword)

    def test_keyword_analysis_is_deterministic_without_external_ai(self):
        kernel = EcosystemKernel()

        first = kernel.seo_agent.analyze_keywords(
            seed_keyword="ai copywriting"
        )
        second = kernel.seo_agent.analyze_keywords(
            seed_keyword="ai copywriting"
        )

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
