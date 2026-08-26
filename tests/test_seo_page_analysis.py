import unittest

from ecosystem_core.kernel import EcosystemKernel


class SEOPageAnalysisTests(unittest.TestCase):

    def test_page_analysis_returns_expected_structure(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_page(
            url="https://example.com/ai-copywriting",
            title="AI Copywriting Tools",
            headings=[
                "AI Copywriting Tools",
                "Create Better Marketing Copy",
            ],
            content=(
                "AI copywriting tools help businesses create effective "
                "marketing content faster."
            ),
            target_keyword="ai copywriting",
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["url"], "https://example.com/ai-copywriting")
        self.assertIn("score", result)
        self.assertIn("keyword", result)
        self.assertIn("checks", result)
        self.assertIn("recommendations", result)

    def test_page_analysis_checks_title(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_page(
            url="https://example.com",
            title="AI Copywriting Tools",
            headings=[],
            content="AI copywriting tools help businesses.",
            target_keyword="ai copywriting",
        )

        self.assertIn("title", result["checks"])

    def test_page_analysis_checks_heading_coverage(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_page(
            url="https://example.com",
            title="AI Copywriting Tools",
            headings=["Create Better Copy"],
            content="AI copywriting tools help businesses.",
            target_keyword="ai copywriting",
        )

        self.assertIn("headings", result["checks"])

    def test_page_analysis_is_deterministic_without_external_ai(self):
        kernel = EcosystemKernel()

        kwargs = {
            "url": "https://example.com",
            "title": "AI Copywriting Tools",
            "headings": ["AI Copywriting"],
            "content": "AI copywriting tools help businesses create content.",
            "target_keyword": "ai copywriting",
        }

        first = kernel.seo_agent.analyze_page(**kwargs)
        second = kernel.seo_agent.analyze_page(**kwargs)

        self.assertEqual(
            first["score"],
            second["score"],
        )
        self.assertEqual(
            first["checks"],
            second["checks"],
        )


if __name__ == "__main__":
    unittest.main()
