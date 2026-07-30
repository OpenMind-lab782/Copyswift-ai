"""
AI Campaign Evaluation Engine
"""

import json


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


def parse_evaluation(text):
    try:
        return json.loads(text)
    except Exception:
        return None
