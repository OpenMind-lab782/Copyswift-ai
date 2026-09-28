"""
AI Campaign Evaluation Engine
"""

import json
import math


_SCORE_FIELDS = (
    "overall",
    "hook",
    "clarity",
    "cta",
    "urgency",
    "trust",
    "emotional_appeal",
    "benefit",
)

_REQUIRED_FIELDS = frozenset(
    _SCORE_FIELDS + ("reasoning", "strengths", "improvement_tips")
)


def build_evaluation_prompt(campaign):
    return f"""
You are an expert marketing strategist.

Evaluate the following marketing campaign.

Campaign:

{campaign}

Return ONLY valid JSON using this schema:

{{
  "overall": 0,
  "hook": 0,
  "clarity": 0,
  "cta": 0,
  "urgency": 0,
  "trust": 0,
  "emotional_appeal": 0,
  "benefit": 0,
  "reasoning": "",
  "strengths": [],
  "improvement_tips": []
}}

Rules:

- Scores must be between 0 and 100.
- Be objective.
- Base the scores on marketing quality.
- Do not include markdown.
- Output JSON only.
"""


def _valid_score(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and 0 <= value <= 100
    )


def parse_evaluation(text):
    try:
        parsed = json.loads(text)
    except (TypeError, ValueError):
        return None

    if not isinstance(parsed, dict):
        return None

    if set(parsed) != _REQUIRED_FIELDS:
        return None

    if not all(_valid_score(parsed[field]) for field in _SCORE_FIELDS):
        return None

    if not isinstance(parsed["reasoning"], str):
        return None

    if not all(isinstance(item, str) for item in parsed["strengths"]):
        return None

    if not all(
        isinstance(item, str) for item in parsed["improvement_tips"]
    ):
        return None

    return parsed
