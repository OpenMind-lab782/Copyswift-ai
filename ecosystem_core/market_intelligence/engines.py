"""
CopySwiftAI Market Intelligence — generic, domain-agnostic engines.

These three engines (MemoryEngine, EvaluationEngine, StrategyEngine)
are intentionally NOT specific to marketing/ad-copy. Each takes a
domain "schema" describing what it should remember, evaluate, or
recommend for a particular product area. The marketing domain schema
(brand voice, campaign scoring rubric, ad-copy strategy fields) is
just the first specialization plugged in — other CopySwiftAI
ecosystem products (SwiftRide, SwiftSteps, etc.) can define their own
schemas and reuse the same underlying engines rather than each
product reimplementing memory/evaluation/strategy logic from scratch.

This is deliberately separate from payment_engine/core/market_brain.py
and market_strategist.py, which are unrelated trading-market classes
(bullish/bearish/buy/sell logic for the future Forex/Arbitrage bot).
"""

import json


class MemoryEngine:
    """Generic, schema-driven memory formatter.

    A schema is a list of (title, key) tuples describing which
    fields to pull from an entity's profile dict, and what label to
    show each one under when formatting it into an AI-prompt-ready
    text block.
    """

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
        """Format a list of past structured outcomes into a
        memory-block string, so future prompts can be informed by
        what has actually worked before, not just static profile
        fields.

        Each record's shape is domain-defined (e.g. a past
        high-scoring campaign with its winning variation, score
        breakdown, and generated strategy) - this formatter is
        intentionally simple and generic; it does not assume any
        particular record structure beyond being displayable.
        """

        if not records:
            return ""

        lines = ["Learned Patterns From Past High Performers:"]
        for record in records[:max_records]:
            lines.append(f"- {record}")

        return "\n".join(lines)


class EvaluationEngine:
    """Generic AI-first evaluator with heuristic fallback.

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

    def evaluate(self, content, model=None):
        """Evaluate content via AI first, falling back to heuristic
        scoring if the AI call fails or returns unusable output."""

        if self.provider is not None:
            try:
                prompt = self.rubric["ai_prompt_template"].format(
                    content=content
                )
                result = self.provider.generate_json(
                    prompt, model=model
                )
                if isinstance(result, dict) and "overall" in result:
                    result["evaluation_source"] = "ai"
                    return result
            except Exception:
                pass

        fallback = self.heuristic_score(content)
        fallback["evaluation_source"] = "heuristic"
        return fallback

    def evaluate_many(self, items, model=None):
        """Evaluate multiple candidate items individually (e.g. ad
        copy variations, alternative driver-response drafts, etc.),
        returning a per-item score plus identification of the
        strongest candidate. Generic across any domain that needs
        to compare several outputs rather than treat them as one
        blob."""

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
        """Rule-based fallback scoring using the rubric's keyword
        banks. Each dimension starts at a base score and gains
        points per matching keyword found in the content."""

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

        # Special-cased structural bonuses, applied only if the
        # dimension exists in this rubric (keeps this generic for
        # rubrics that don't define a "hook"/"clarity" dimension).
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
    """Generic AI-driven strategy generator with safe empty fallback.

    A schema defines:
      - "fields": list of field names the strategy object should
        contain
      - "ai_prompt_template": a format-string template used to ask
        an AI provider to produce a JSON strategy object
    """

    def __init__(self, schema, provider=None):
        self.schema = schema
        self.provider = provider

    def default(self):
        """Return the schema's empty/default strategy shape."""

        return {field: "" for field in self.schema.get("fields", [])}

    def generate(self, context, model=None, evaluation=None):
        """Generate a structured strategy via AI, falling back to
        the schema's empty default if generation fails.

        If `evaluation` is supplied (e.g. the output of an
        EvaluationEngine's evaluate() or evaluate_many()), its
        findings are woven into the prompt so the strategy is
        grounded in actually-detected strengths/weaknesses rather
        than generated blind from content alone.
        """

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
