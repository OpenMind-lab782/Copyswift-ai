import json
import unittest

from brain.ai_evaluator import parse_evaluation


def _evaluation(**overrides):
    value = {
        "overall": 78,
        "hook": 80,
        "clarity": 90,
        "cta": 70,
        "urgency": 60,
        "trust": 80,
        "emotional_appeal": 75,
        "benefit": 80,
        "reasoning": "Solid campaign.",
        "strengths": ["Clear offer"],
        "improvement_tips": ["Strengthen urgency"],
    }
    value.update(overrides)
    return json.dumps(value)


class TestAIEvaluationParsing(unittest.TestCase):
    def test_accepts_valid_bounded_scores(self):
        parsed = parse_evaluation(_evaluation())
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["overall"], 78)

    def test_rejects_score_above_100(self):
        self.assertIsNone(parse_evaluation(_evaluation(overall=175)))

    def test_rejects_score_below_zero(self):
        self.assertIsNone(parse_evaluation(_evaluation(overall=-1)))

    def test_rejects_non_numeric_score(self):
        self.assertIsNone(parse_evaluation(_evaluation(overall="100")))

    def test_rejects_boolean_score(self):
        self.assertIsNone(parse_evaluation(_evaluation(overall=True)))

    def test_rejects_non_finite_score(self):
        self.assertIsNone(parse_evaluation(_evaluation(overall=float("nan"))))

    def test_rejects_missing_required_field(self):
        value = json.loads(_evaluation())
        del value["benefit"]
        self.assertIsNone(parse_evaluation(json.dumps(value)))

    def test_rejects_unexpected_field(self):
        value = json.loads(_evaluation())
        value["unexpected"] = "invalid"
        self.assertIsNone(parse_evaluation(json.dumps(value)))

    def test_rejects_invalid_reasoning_type(self):
        self.assertIsNone(parse_evaluation(_evaluation(reasoning=123)))

    def test_rejects_invalid_strength_type(self):
        self.assertIsNone(parse_evaluation(_evaluation(strengths=["ok", 1])))

    def test_rejects_invalid_improvement_tip_type(self):
        self.assertIsNone(
            parse_evaluation(_evaluation(improvement_tips=["ok", 1]))
        )


if __name__ == "__main__":
    unittest.main()
