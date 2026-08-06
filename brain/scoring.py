"""
Enhanced Campaign Scoring Engine
"""

import re

CTA_WORDS = [
    "buy", "order", "shop", "call", "contact",
    "register", "sign up", "book", "start",
    "join", "learn more", "whatsapp", "message",
    "get started", "try now"
]

URGENCY_WORDS = [
    "today", "now", "limited", "offer",
    "ending", "last chance", "don't miss",
    "exclusive", "only", "deadline"
]

TRUST_WORDS = [
    "guarantee", "trusted", "official",
    "quality", "proven", "secure",
    "reliable", "professional"
]

EMOTION_WORDS = [
    "love", "easy", "save", "grow",
    "success", "dream", "happy",
    "powerful", "boost", "win"
]

BENEFIT_WORDS = [
    "increase", "improve", "faster",
    "better", "more sales", "results",
    "customers", "business", "profit",
    "convert", "marketing"
]


def _count_matches(text, words):
    text = text.lower()
    return sum(1 for w in words if w in text)


def score_campaign(text):
    text = text.strip()

    words = text.split()
    word_count = len(words)

    # Hook
    hook = 60
    if "!" in text:
        hook += 10
    if "?" in text:
        hook += 10
    if text[:1].isupper():
        hook += 5
    if len(text.splitlines()) > 2:
        hook += 5
    hook = min(hook, 100)

    # Clarity
    clarity = 100
    if word_count > 80:
        clarity -= min(30, word_count - 80)
    clarity = max(60, clarity)

    # CTA
    cta_matches = _count_matches(text, CTA_WORDS)
    cta = min(100, 50 + cta_matches * 15)

    # Urgency
    urgency_matches = _count_matches(text, URGENCY_WORDS)
    urgency = min(100, 60 + urgency_matches * 10)

    # Trust
    trust_matches = _count_matches(text, TRUST_WORDS)
    trust = min(100, 70 + trust_matches * 10)

    # Emotion
    emotion_matches = _count_matches(text, EMOTION_WORDS)
    emotion = min(100, 60 + emotion_matches * 10)

    # Benefits
    benefit_matches = _count_matches(text, BENEFIT_WORDS)
    benefit = min(100, 60 + benefit_matches * 10)

    overall = round(
        (
            hook +
            clarity +
            cta +
            urgency +
            trust +
            emotion +
            benefit
        ) / 7
    )

    tips = []

    if cta < 90:
        tips.append("Strengthen the call-to-action.")

    if urgency < 80:
        tips.append("Increase urgency.")

    if trust < 80:
        tips.append("Add more trust signals.")

    if emotion < 80:
        tips.append("Use more emotional language.")

    if benefit < 80:
        tips.append("Highlight customer benefits more clearly.")

    strengths = []

    if hook >= 80:
        strengths.append("Strong opening hook")

    if clarity >= 95:
        strengths.append("Excellent clarity")

    if cta >= 90:
        strengths.append("Clear call-to-action")

    if urgency >= 90:
        strengths.append("Creates urgency")

    if trust >= 90:
        strengths.append("Builds customer trust")

    if benefit >= 90:
        strengths.append("Strong value proposition")

    return {
        "overall": overall,
        "hook": hook,
        "clarity": clarity,
        "cta": cta,
        "urgency": urgency,
        "trust": trust,
        "emotional_appeal": emotion,
        "benefit": benefit,
        "strengths": strengths,
        "improvement_tips": tips,
    }
