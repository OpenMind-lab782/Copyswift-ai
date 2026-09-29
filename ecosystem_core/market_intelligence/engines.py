"""
CopySwiftAI Market Intelligence — generic, domain-agnostic engines.

These three engines (MemoryEngine, EvaluationEngine, StrategyEngine)
are intentionally NOT specific to marketing/ad-copy. Each takes a
domain "schema" describing what it should remember, evaluate, or
recommend for a particular product area. The marketing domain schema
(brand voice, campaign scoring rubric, ad-copy strategy fields) is
just the first specialization plugged into the generic engines.

This is deliberately separate from payment_engine/core/market_brain.py
and market_strategist.py, which are unrelated trading-market classes.
"""

import json
import math


class MemoryEngine:
    """Generic, schema-driven memory formatter."""

    def __init__(self, schema, provider=None):
        self.schema = schema
        self.provider = provider

    def format_context(self, profile):
        """Render a profile dict into a memory-block string."""

        if not profile:
            return ""

        sections = []
        for title, key in self.schema:
            value = profile.get(key)
            if value:
                sections.append(f"{title}: {value}")

        return "\n".join(sections)

    def format_learned_patterns(self, records, max_records=3):
        """Format past structured outcomes into a prompt-ready block."""

        if not records:
            return ""

        lines = ["Learned Patterns From Past High Performers:"]
        for record in records[:max_records]:
            lines.append(f"- {record}")

        return "\n".join(lines)


class EvaluationEngine:
    """Generic AI-first evaluator with bounded-score validation.

    A rubric defines:
      - "dimensions": dict of dimension_name -> list of keywords
        used for heuristic (non-AI) scoring
      - "ai_prompt_template": a format-string template used to ask
        an AI provider to score content against the same dimensions,
        returning JSON
    """

    def __init__(self, rubric, provider=None):
        self.rubric = rubric
        self.provider = provider

    def _valid_ai_result(self, result):
        """Accept AI scores only when every supplied score is 0..100."""

        if not isinstance(result, dict) or "overall" not in result:
            return False

        score_fields = {"overall", *self.rubric.get("dimensions", {})}
        for field in score_fields:
            if field not in result:
                continue
            value = result[field]
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or not 0 <= value <= 100
            ):
                return False

        return True

    def evaluate(self, content, model=None):
        """Evaluate content via AI, falling back on invalid AI output."""

        if self.provider is not None:
            try:
                prompt = self.rubric["ai_prompt_template"].format(
                    content=content
                )
                result = self.provider.generate_json(
                    prompt, model=model
                )
                if self._valid_ai_result(result):
                    result["evaluation_source"] = "ai"
                    return result
            except Exception:
                pass

        fallback = self.heuristic_score(content)
        fallback["evaluation_source"] = "heuristic"
        return fallback

    def evaluate_many(self, items, model=None):
        """Evaluate multiple candidate items and identify the strongest."""

        results = []
        for item in items:
            score = self.evaluate(item, model=model)
            results.append({"content": item, "score": score})

        if not results:
            return {"items": [], "best_index": None, "best": None}

        best_index = max(
            range(len(results)),
            key=lambda i: results[i]["score"].get("overall", 0),
        )

        return {
            "items": results,
            "best_index": best_index,
            "best": results[best_index],
        }

    def heuristic_score(self, content):
        """Rule-based fallback scoring using the rubric's keyword banks."""

        text = (content or "").strip()
        text_lower = text.lower()
        words = text.split()
        word_count = len(words)

        dimensions = self.rubric.get("dimensions", {})
        scores = {}

        for name, config in dimensions.items():
            base = config.get("base", 60)
            per_match = config.get("per_match", 10)
            cap = config.get("cap", 100)
            keywords = config.get("keywords", [])

            matches = sum(1 for w in keywords if w in text_lower)
            score = min(cap, base + matches * per_match)
            scores[name] = score

        if "hook" in scores:
            hook = scores["hook"]
            if "!" in text:
                hook += 10
            if "?" in text:
                hook += 10
            if text[:1].isupper():
                hook += 5
            if len(text.splitlines()) > 2:
                hook += 5
            scores["hook"] = min(100, hook)

        if "clarity" in scores:
            clarity = scores["clarity"]
            if word_count > 80:
                clarity -= min(30, word_count - 80)
            scores["clarity"] = max(60, clarity)

        overall = (
            round(sum(scores.values()) / len(scores))
            if scores else 0
        )

        tips = []
        strengths = []
        for name, config in dimensions.items():
            score = scores.get(name, 0)
            tip = config.get("tip")
            strength = config.get("strength")
            tip_threshold = config.get("tip_below", 80)
            strength_threshold = config.get("strength_at", 90)

            if tip and score < tip_threshold:
                tips.append(tip)
            if strength and score >= strength_threshold:
                strengths.append(strength)

        return {
            "overall": overall,
            **scores,
            "strengths": strengths,
            "improvement_tips": tips,
        }


class StrategyEngine:
    """Generic AI-driven strategy generator with safe empty fallback."""

    def __init__(self, schema, provider=None):
        self.schema = schema
        self.provider = provider

    def default(self):
        """Return the schema's empty/default strategy shape."""

        return {field: "" for field in self.schema.get("fields", [])}

    def generate(self, context, model=None, evaluation=None):
        """Generate a structured strategy with safe fallback."""

        if self.provider is not None:
            try:
                full_context = context
                if evaluation:
                    full_context = (
                        context
                        + "\n\nEvaluation findings (use these to "
                        + "ground your recommendations):\n"
                        + json.dumps(evaluation)
                    )

                prompt = self.schema["ai_prompt_template"].format(
                    context=full_context
                )
                result = self.provider.generate_json(
                    prompt, model=model
                )
                if isinstance(result, dict):
                    merged = self.default()
                    merged.update(result)
                    merged["strategy_source"] = "ai"
                    return merged
            except Exception:
                pass

        fallback = self.default()
        fallback["strategy_source"] = "default"
        return fallback
