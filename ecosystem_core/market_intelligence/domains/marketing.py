"""
Marketing domain schema for CopySwiftAI Market Intelligence.

This is the first domain plugged into the generic MemoryEngine,
EvaluationEngine, and StrategyEngine. It carries over the exact
field lists and keyword banks from the original brain/ module
(memory.py, scoring.py) so existing behavior is preserved, now
expressed as a reusable schema rather than hardcoded logic.
"""

MARKETING_MEMORY_SCHEMA = [
    ("Brand Voice", "brand_voice"),
    ("Brand Style", "brand_style"),
    ("Business Goal", "brand_goal"),
    ("Keywords", "brand_keywords"),
    ("CTA", "brand_cta"),
    ("Winning Headlines", "winning_headlines"),
    ("Winning CTAs", "winning_ctas"),
    ("Customer Objections", "customer_objections"),
    ("Marketing Notes", "marketing_notes"),
    ("Seasonal Campaigns", "seasonal_campaigns"),
    ("Last Campaign", "last_campaign_summary"),
]

CTA_WORDS = [
    "buy", "order", "shop", "call", "contact",
    "register", "sign up", "book", "start",
    "join", "learn more", "whatsapp", "message",
    "get started", "try now",
]

URGENCY_WORDS = [
    "today", "now", "limited", "offer",
    "ending", "last chance", "don't miss",
    "exclusive", "only", "deadline",
]

TRUST_WORDS = [
    "guarantee", "trusted", "official",
    "quality", "proven", "secure",
    "reliable", "professional",
]

EMOTION_WORDS = [
    "love", "easy", "save", "grow",
    "success", "dream", "happy",
    "powerful", "boost", "win",
]

BENEFIT_WORDS = [
    "increase", "improve", "faster",
    "better", "more sales", "results",
    "customers", "business", "profit",
    "convert", "marketing",
]

MARKETING_RUBRIC = {
    "dimensions": {
        "hook": {
            "base": 60, "per_match": 0, "cap": 100, "keywords": [],
            "strength": "Strong opening hook", "strength_at": 80,
        },
        "clarity": {
            "base": 100, "per_match": 0, "cap": 100, "keywords": [],
            "strength": "Excellent clarity", "strength_at": 95,
        },
        "cta": {
            "base": 50, "per_match": 15, "cap": 100,
            "keywords": CTA_WORDS,
            "tip": "Strengthen the call-to-action.", "tip_below": 90,
            "strength": "Clear call-to-action", "strength_at": 90,
        },
        "urgency": {
            "base": 60, "per_match": 10, "cap": 100,
            "keywords": URGENCY_WORDS,
            "tip": "Increase urgency.", "tip_below": 80,
            "strength": "Creates urgency", "strength_at": 90,
        },
        "trust": {
            "base": 70, "per_match": 10, "cap": 100,
            "keywords": TRUST_WORDS,
            "tip": "Add more trust signals.", "tip_below": 80,
            "strength": "Builds customer trust", "strength_at": 90,
        },
        "emotional_appeal": {
            "base": 60, "per_match": 10, "cap": 100,
            "keywords": EMOTION_WORDS,
            "tip": "Use more emotional language.", "tip_below": 80,
        },
        "benefit": {
            "base": 60, "per_match": 10, "cap": 100,
            "keywords": BENEFIT_WORDS,
            "tip": "Highlight customer benefits more clearly.",
            "tip_below": 80,
            "strength": "Strong value proposition", "strength_at": 90,
        },
    },
    "ai_prompt_template": """
You are an expert marketing strategist.
Evaluate the following marketing campaign.
Campaign:
{content}
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
""",
}

MARKETING_STRATEGY_SCHEMA = {
    "fields": [
        "objective",
        "recommended_platform",
        "recommended_audience",
        "best_posting_time",
        "marketing_tip",
        "follow_up",
        "ab_test",
    ],
    "ai_prompt_template": """
You are an expert marketing strategist.
Given the following campaign context, recommend a concrete
marketing strategy.
Context:
{context}
Return ONLY valid JSON using this schema:
{{
  "objective": "",
  "recommended_platform": "",
  "recommended_audience": "",
  "best_posting_time": "",
  "marketing_tip": "",
  "follow_up": "",
  "ab_test": ""
}}
Rules:
- Be concrete and specific, not generic.
- Do not include markdown.
- Output JSON only.
""",
}
