"""
Swift Payment Engine — Language Quality Engine.

Evaluates generated marketing language using the configured AI provider.

The engine has a deterministic fallback so a temporary AI outage does not
break downstream application workflows.
"""

import re


class LanguageQualityEngine:
    """
    AI-backed language quality evaluator.
    """

    SCORE_FIELDS = (
        "overall",
        "fluency",
        "grammar",
        "naturalness",
        "clarity",
        "cultural_consistency",
    )

    def __init__(self, provider):
        self.provider = provider

    def _fallback(self, text, language, context):
        """
        Deterministic fallback evaluation.

        This is intentionally conservative and does not pretend to be
        equivalent to an AI linguistic evaluation.
        """
        text = (text or "").strip()

        if not text:
            overall = 0
            fluency = 0
            grammar = 0
            naturalness = 0
            clarity = 0
        else:
            words = re.findall(r"\b\w+[\w'-]*\b", text)
            word_count = len(words)

            sentences = [
                part.strip()
                for part in re.split(r"[.!?]+", text)
                if part.strip()
            ]

            long_words = sum(1 for word in words if len(word) > 18)
            sentence_count = max(len(sentences), 1)

            clarity = min(
                100,
                70
                + min(20, word_count)
                - min(20, long_words * 3),
            )

            fluency = min(
                100,
                72
                + min(18, sentence_count * 4)
                - min(20, long_words * 2),
            )

            grammar = 85

            if text[-1:] not in ".!?":
                grammar -= 5

            if "  " in text:
                grammar -= 5

            naturalness = min(
                100,
                max(0, (fluency + clarity) // 2),
            )

            overall = min(
                100,
                max(
                    0,
                    (
                        fluency
                        + grammar
                        + naturalness
                        + clarity
                    ) // 4,
                ),
            )

        return {
            "status": "evaluated",
            "language": language,
            "context": context,
            "overall": overall,
            "fluency": fluency,
            "grammar": grammar,
            "naturalness": naturalness,
            "clarity": clarity,
            "cultural_consistency": 75 if text else 0,
            "evaluation_source": "heuristic",
            "strengths": [],
            "improvement_tips": [
                "Use AI evaluation for deeper linguistic and cultural analysis."
            ],
        }

    def _normalize(self, result, language, context):
        if not isinstance(result, dict):
            raise ValueError("AI quality response must be an object.")

        normalized = {
            "status": "evaluated",
            "language": result.get("language", language),
            "context": result.get("context", context),
            "overall": result.get("overall", 0),
            "fluency": result.get("fluency", 0),
            "grammar": result.get("grammar", 0),
            "naturalness": result.get("naturalness", 0),
            "clarity": result.get("clarity", 0),
            "cultural_consistency": result.get(
                "cultural_consistency",
                0,
            ),
            "evaluation_source": "ai",
            "strengths": result.get("strengths", []),
            "improvement_tips": result.get(
                "improvement_tips",
                [],
            ),
        }

        for field in self.SCORE_FIELDS:
            try:
                score = float(normalized[field])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Invalid quality score: {field}"
                )

            normalized[field] = max(0, min(100, round(score)))

        if not isinstance(normalized["strengths"], list):
            normalized["strengths"] = []

        if not isinstance(normalized["improvement_tips"], list):
            normalized["improvement_tips"] = []

        return normalized

    def evaluate(
        self,
        text,
        language="English",
        context="general content",
    ):
        text = (text or "").strip()

        prompt = f"""
Evaluate the following text for language quality.

Language:
{language}

Context:
{context}

Text:
{text}

Return ONLY valid JSON using exactly this structure:

{{
  "language": "{language}",
  "context": "{context}",
  "overall": 0,
  "fluency": 0,
  "grammar": 0,
  "naturalness": 0,
  "clarity": 0,
  "cultural_consistency": 0,
  "strengths": [],
  "improvement_tips": []
}}

Rules:

- Every score must be an integer from 0 to 100.
- Evaluate the requested language.
- Evaluate grammar, fluency, naturalness, clarity and cultural consistency.
- Consider the supplied context.
- Be objective.
- Do not invent facts about the text.
- Return JSON only.
""".strip()

        try:
            result = self.provider.generate_json(
                prompt=prompt,
                temperature=0.1,
                max_tokens=1000,
            )

            return self._normalize(
                result,
                language=language,
                context=context,
            )

        except Exception:
            return self._fallback(
                text=text,
                language=language,
                context=context,
            )
