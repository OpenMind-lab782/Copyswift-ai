import unittest

from ecosystem_core.kernel import EcosystemKernel


class SEOContentAnalysisErrorTests(unittest.TestCase):

    def test_empty_content_returns_zero_score(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_content(
            keyword="seo",
            content="",
        )

        self.assertEqual(
            result["score"],
            0,
        )
        self.assertEqual(
            result["word_count"],
            0,
        )
        self.assertEqual(
            result["keyword_occurrences"],
            0,
        )

    def test_empty_keyword_is_handled_cleanly(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_content(
            keyword="",
            content="SEO helps businesses improve visibility.",
        )

        self.assertEqual(
            result["keyword"],
            "",
        )
        self.assertEqual(
            result["keyword_occurrences"],
            0,
        )
        self.assertIsInstance(
            result["recommendations"],
            list,
        )

    def test_keyword_matching_is_case_insensitive(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_content(
            keyword="SEO",
            content="seo improves visibility. SEO builds trust.",
        )

        self.assertEqual(
            result["keyword_occurrences"],
            2,
        )

    def test_excessive_keyword_repetition_generates_recommendation(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_content(
            keyword="seo",
            content=(
                "SEO SEO SEO SEO SEO SEO SEO SEO SEO SEO"
            ),
        )

        self.assertGreater(
            result["keyword_density"],
            3,
        )

        self.assertTrue(
            any(
                "keyword repetition" in recommendation.lower()
                for recommendation in result["recommendations"]
            )
        )


if __name__ == "__main__":
    unittest.main()
