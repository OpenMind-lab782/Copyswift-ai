"""
Campaign Scoring Engine
"""

def score_campaign(text):
    score = 0

    if "!" in text:
        score += 10

    if "today" in text.lower():
        score += 10

    if "free" in text.lower():
        score += 10

    return {
        "score": score,
        "max_score": 100
    }
