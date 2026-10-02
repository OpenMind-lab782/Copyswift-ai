import math
import unittest

from ecosystem_core.market_intelligence.engines import EvaluationEngine


RUBRIC = {
    "dimensions": {
        "clarity": {"base": 60, "cap": 100, "keywords": []},
    },
    "ai_prompt_template": "Evaluate: {content}",
}


class StubProvider:
    def __init__(self, result):
        self.result = result

    def generate_json(self, prompt, model=None):
        return dict(self.result)


class TestEvaluationEngineScoreValidation(unittest.TestCase):
    def test_accepts_bounded_ai_score(self):
        engine = EvaluationEngine(
            RUBRIC,
            provider=StubProvider({"overall": 100, "clarity": 90}),
        )

        result = engine.evaluate("Valid")

        self.assertEqual(result["overall"], 100)
        self.assertEqual(result["evaluation_source"], "ai")

    def test_rejects_ai_score_above_100_and_uses_heuristic(self):
        engine = EvaluationEngine(
            RUBRIC,
            provider=StubProvider({"overall": 170, "clarity": 90}),
        )

        result = engine.evaluate("Fallback")

        self.assertEqual(result["evaluation_source"], "heuristic")
        self.assertLessEqual(result["overall"], 100)

    def test_rejects_negative_ai_score_and_uses_heuristic(self):
        engine = EvaluationEngine(
            RUBRIC,
            provider=StubProvider({"overall": -1, "clarity": 90}),
        )

        result = engine.evaluate("Fallback")

        self.assertEqual(result["evaluation_source"], "heuristic")
        self.assertGreaterEqual(result["overall"], 0)

    def test_rejects_boolean_ai_score_and_uses_heuristic(self):
        engine = EvaluationEngine(
            RUBRIC,
            provider=StubProvider({"overall": True, "clarity": 90}),
        )

        result = engine.evaluate("Fallback")

        self.assertEqual(result["evaluation_source"], "heuristic")

    def test_rejects_nonfinite_ai_score_and_uses_heuristic(self):
        engine = EvaluationEngine(
            RUBRIC,
            provider=StubProvider({"overall": math.nan, "clarity": 90}),
        )

        result = engine.evaluate("Fallback")

        self.assertEqual(result["evaluation_source"], "heuristic")

    def test_rejects_out_of_range_dimension_score(self):
        engine = EvaluationEngine(
            RUBRIC,
            provider=StubProvider({"overall": 80, "clarity": 101}),
        )

        result = engine.evaluate("Fallback")

        self.assertEqual(result["evaluation_source"], "heuristic")

    def test_evaluate_many_cannot_return_out_of_range_ai_score(self):
        engine = EvaluationEngine(
            RUBRIC,
            provider=StubProvider({"overall": 175, "clarity": 90}),
        )

        result = engine.evaluate_many(["One", "Two"])

        for item in result["items"]:
            self.assertLessEqual(item["score"]["overall"], 100)
            self.assertEqual(item["score"]["evaluation_source"], "heuristic")


if __name__ == "__main__":
    unittest.main()
