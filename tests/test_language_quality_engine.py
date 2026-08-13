import unittest

from intelligence.quality_engine import LanguageQualityEngine


class FakeProvider:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.prompts = []

    def generate_json(self, prompt, **kwargs):
        self.prompts.append(prompt)

        if self.error:
            raise self.error

        return self.response


class TestLanguageQualityEngine(unittest.TestCase):

    def test_empty_text_uses_fallback(self):
        provider = FakeProvider()
        engine = LanguageQualityEngine(provider)

        result = engine.evaluate(
            "",
            language="English",
            context="marketing copy",
        )

        self.assertEqual(result["status"], "evaluated")
        self.assertEqual(result["language"], "English")
        self.assertEqual(result["overall"], 0)
        self.assertEqual(result["fluency"], 0)
        self.assertEqual(result["grammar"], 0)
        self.assertEqual(result["naturalness"], 0)
        self.assertEqual(result["clarity"], 0)
        self.assertEqual(result["evaluation_source"], "heuristic")

    def test_fallback_evaluation(self):
        provider = FakeProvider(
            error=RuntimeError("simulated AI outage")
        )

        engine = LanguageQualityEngine(provider)

        result = engine.evaluate(
            "This is a simple sentence.",
            language="English",
            context="general content",
        )

        self.assertEqual(result["status"], "evaluated")
        self.assertEqual(result["language"], "English")
        self.assertEqual(result["context"], "general content")
        self.assertEqual(result["evaluation_source"], "heuristic")
        self.assertGreater(result["overall"], 0)

        for field in (
            "overall",
            "fluency",
            "grammar",
            "naturalness",
            "clarity",
            "cultural_consistency",
        ):
            self.assertGreaterEqual(result[field], 0)
            self.assertLessEqual(result[field], 100)

    def test_ai_evaluation(self):
        provider = FakeProvider(
            response={
                "language": "English",
                "context": "marketing copy",
                "overall": 91,
                "fluency": 94,
                "grammar": 92,
                "naturalness": 90,
                "clarity": 93,
                "cultural_consistency": 88,
                "strengths": ["Clear message"],
                "improvement_tips": ["Improve the CTA"],
            }
        )

        engine = LanguageQualityEngine(provider)

        result = engine.evaluate(
            "Build your business with Swift.",
            language="English",
            context="marketing copy",
        )

        self.assertEqual(result["status"], "evaluated")
        self.assertEqual(result["overall"], 91)
        self.assertEqual(result["fluency"], 94)
        self.assertEqual(result["grammar"], 92)
        self.assertEqual(result["naturalness"], 90)
        self.assertEqual(result["clarity"], 93)
        self.assertEqual(result["cultural_consistency"], 88)
        self.assertEqual(result["evaluation_source"], "ai")
        self.assertEqual(result["strengths"], ["Clear message"])
        self.assertEqual(
            result["improvement_tips"],
            ["Improve the CTA"],
        )
        self.assertEqual(len(provider.prompts), 1)

    def test_ai_scores_are_normalized(self):
        provider = FakeProvider(
            response={
                "language": "English",
                "overall": 150,
                "fluency": -20,
                "grammar": "85",
                "naturalness": 101.8,
                "clarity": 72.4,
                "cultural_consistency": 50,
                "strengths": "not a list",
                "improvement_tips": "not a list",
            }
        )

        engine = LanguageQualityEngine(provider)

        result = engine.evaluate(
            "Normalize these scores.",
            language="English",
        )

        self.assertEqual(result["overall"], 100)
        self.assertEqual(result["fluency"], 0)
        self.assertEqual(result["grammar"], 85)
        self.assertEqual(result["naturalness"], 100)
        self.assertEqual(result["clarity"], 72)
        self.assertEqual(result["cultural_consistency"], 50)
        self.assertEqual(result["strengths"], [])
        self.assertEqual(result["improvement_tips"], [])
        self.assertEqual(result["evaluation_source"], "ai")

    def test_invalid_ai_response_falls_back(self):
        provider = FakeProvider(
            response="this is not a valid structured response"
        )

        engine = LanguageQualityEngine(provider)

        result = engine.evaluate(
            "Hello world.",
            language="English",
        )

        self.assertEqual(result["status"], "evaluated")
        self.assertEqual(result["evaluation_source"], "heuristic")
        self.assertGreaterEqual(result["overall"], 0)

    def test_provider_exception_falls_back(self):
        provider = FakeProvider(
            error=RuntimeError("network failure")
        )

        engine = LanguageQualityEngine(provider)

        result = engine.evaluate(
            "Welcome to our service.",
            language="English",
        )

        self.assertEqual(result["evaluation_source"], "heuristic")
        self.assertIn("improvement_tips", result)

    def test_required_output_structure(self):
        provider = FakeProvider(
            error=RuntimeError("offline")
        )

        engine = LanguageQualityEngine(provider)

        result = engine.evaluate(
            "Grow your business with better marketing.",
            language="English",
            context="marketing copy",
        )

        required_fields = {
            "status",
            "language",
            "context",
            "overall",
            "fluency",
            "grammar",
            "naturalness",
            "clarity",
            "cultural_consistency",
            "evaluation_source",
            "strengths",
            "improvement_tips",
        }

        self.assertTrue(required_fields.issubset(result.keys()))

    def test_markdown_json_response_is_supported_by_provider_contract(self):
        class MarkdownProvider:
            def __init__(self):
                self.prompts = []

            def generate_json(self, prompt, **kwargs):
                self.prompts.append(prompt)

                return {
                    "language": "English",
                    "overall": 80,
                    "fluency": 80,
                    "grammar": 80,
                    "naturalness": 80,
                    "clarity": 80,
                    "cultural_consistency": 80,
                    "strengths": [],
                    "improvement_tips": [],
                }

        provider = MarkdownProvider()
        engine = LanguageQualityEngine(provider)

        result = engine.evaluate(
            "Hello world.",
            language="English",
        )

        self.assertEqual(result["overall"], 80)
        self.assertEqual(result["evaluation_source"], "ai")
        self.assertEqual(len(provider.prompts), 1)


if __name__ == "__main__":
    unittest.main()
