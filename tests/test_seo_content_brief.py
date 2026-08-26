import unittest

from ecosystem_core.kernel import EcosystemKernel


class SEOContentBriefTests(unittest.TestCase):

    def test_content_brief_returns_expected_structure(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.build_content_brief(
            keyword="ai copywriting tools"
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(
            result["keyword"],
            "ai copywriting tools",
        )
        self.assertIn("search_intent", result)
        self.assertIn("title", result)
        self.assertIn("outline", result)
        self.assertIn("key_points", result)
        self.assertIn("internal_link_topics", result)

    def test_content_brief_has_multiple_outline_sections(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.build_content_brief(
            keyword="ai copywriting tools"
        )

        self.assertGreaterEqual(
            len(result["outline"]),
            4,
        )

    def test_content_brief_is_deterministic(self):
        kernel = EcosystemKernel()

        first = kernel.seo_agent.build_content_brief(
            keyword="ai copywriting tools"
        )
        second = kernel.seo_agent.build_content_brief(
            keyword="ai copywriting tools"
        )

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
