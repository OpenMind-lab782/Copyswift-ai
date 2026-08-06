"""
AI Evaluation Service
"""

from brain.ai_evaluator import (
    build_evaluation_prompt,
    parse_evaluation,
)
from brain.scoring import score_campaign


def evaluate_campaign(client, model, campaign):
    """
    Evaluate a marketing campaign using AI.
    Falls back to heuristic scoring if needed.
    """

    prompt = build_evaluation_prompt(campaign)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert marketing evaluator."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content.strip()

        parsed = parse_evaluation(content)

        if parsed:
            parsed["evaluation_source"] = "ai"
            return parsed

    except Exception:
        pass

    fallback = score_campaign(campaign)
    fallback["evaluation_source"] = "heuristic"

    return fallback
