import unittest

from ecosystem_core.kernel import EcosystemKernel


class SEOContentOptimizationTests(unittest.TestCase):

    def test_content_optimization_returns_expected_structure(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.optimize_content(
            keyword="seo",
            content="SEO helps businesses improve visibility.",
        )

        self.assertIsInstance(result, dict)

        for field in (
            "keyword",
            "original_content",
            "optimized_content",
            "original_analysis",
            "optimized_analysis",
            "changes",
            "recommendations",
        ):
            self.assertIn(field, result)

    def test_content_optimization_preserves_original_content(self):
        kernel = EcosystemKernel()

        content = "SEO helps businesses improve visibility."

        result = kernel.seo_agent.optimize_content(
            keyword="seo",
            content=content,
        )

        self.assertEqual(
            result["original_content"],
            content,
        )

    def test_content_optimization_adds_keyword_when_missing(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.optimize_content(
            keyword="copywriting",
            content="Great content helps businesses communicate with customers.",
        )

        optimized = result["optimized_content"].lower()

        self.assertIn(
            "copywriting",
            optimized,
        )

        self.assertTrue(
            any(
                "keyword" in change.lower()
                for change in result["changes"]
            )
        )

    def test_content_optimization_is_deterministic(self):
        kernel = EcosystemKernel()

        content = (
            "SEO helps businesses improve visibility. "
            "Strong content supports discovery."
        )

        first = kernel.seo_agent.optimize_content(
            keyword="seo",
            content=content,
        )

        second = kernel.seo_agent.optimize_content(
            keyword="seo",
            content=content,
        )

        self.assertEqual(
            first,
            second,
        )

    def test_content_optimization_does_not_mutate_source_value(self):
        kernel = EcosystemKernel()

        content = "SEO helps businesses improve visibility."

        kernel.seo_agent.optimize_content(
            keyword="seo",
            content=content,
        )

        self.assertEqual(
            content,
            "SEO helps businesses improve visibility.",
        )


if __name__ == "__main__":
    unittest.main()
