import unittest

from ecosystem_core.kernel import EcosystemKernel


class SEOContentAnalysisTests(unittest.TestCase):

    def test_content_analysis_returns_expected_structure(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_content(
            keyword="copywriting",
            content=(
                "Copywriting helps businesses communicate clearly. "
                "Effective copywriting improves sales and engagement. "
                "Good copywriting focuses on the reader."
            ),
        )

        self.assertIsInstance(result, dict)

        for field in (
            "keyword",
            "word_count",
            "keyword_occurrences",
            "keyword_density",
            "paragraph_count",
            "sentence_count",
            "score",
            "recommendations",
        ):
            self.assertIn(field, result)

    def test_content_analysis_counts_words(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_content(
            keyword="copywriting",
            content="Copywriting improves sales. Good copywriting builds trust.",
        )

        self.assertEqual(
            result["word_count"],
            7,
        )

    def test_content_analysis_counts_keyword_occurrences(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_content(
            keyword="copywriting",
            content=(
                "Copywriting improves sales. "
                "Good copywriting builds trust. "
                "Copywriting also supports marketing."
            ),
        )

        self.assertEqual(
            result["keyword_occurrences"],
            3,
        )

    def test_content_analysis_calculates_keyword_density(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_content(
            keyword="seo",
            content="SEO helps brands. SEO improves visibility.",
        )

        self.assertEqual(
            result["keyword_occurrences"],
            2,
        )

        self.assertGreater(
            result["keyword_density"],
            0,
        )

    def test_content_analysis_counts_paragraphs_and_sentences(self):
        kernel = EcosystemKernel()

        result = kernel.seo_agent.analyze_content(
            keyword="seo",
            content=(
                "SEO improves visibility. SEO supports discovery.\n\n"
                "Strong SEO also improves relevance."
            ),
        )

        self.assertEqual(
            result["paragraph_count"],
            2,
        )
        self.assertEqual(
            result["sentence_count"],
            3,
        )

    def test_content_analysis_is_deterministic(self):
        kernel = EcosystemKernel()

        content = (
            "SEO improves visibility. "
            "SEO supports discovery. "
            "Strong SEO improves relevance."
        )

        first = kernel.seo_agent.analyze_content(
            keyword="seo",
            content=content,
        )
        second = kernel.seo_agent.analyze_content(
            keyword="seo",
            content=content,
        )

        self.assertEqual(
            first,
            second,
        )


if __name__ == "__main__":
    unittest.main()
