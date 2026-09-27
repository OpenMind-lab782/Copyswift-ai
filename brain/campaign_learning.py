"""
Campaign Learning Engine
"""

def summarize_campaign(text):
    if not text:
        return ""

    return text[:300]


def should_learn(score):
    """
    Learn only from strong campaigns.
    """
    return score.get("overall", 0) >= 90


def learning_summary(score):
    return {
        "learned": should_learn(score),
        "overall_score": score.get("overall", 0),
        "reason": (
            "High-quality campaign saved."
            if should_learn(score)
            else "Campaign below learning threshold."
        ),
    }


def persist_learning(db, profile_id, campaign_text, score, validated=True):
    """
    Save high-quality, validated campaigns into the Business Brain.
    Generated copy must pass the grounding boundary before it becomes memory.
    """
    if not validated:
        return False

    if not should_learn(score):
        return False

    summary = summarize_campaign(campaign_text)

    db.execute("""
        UPDATE business_profiles
        SET
            last_campaign_summary = ?,
            marketing_notes = COALESCE(marketing_notes,'') ||
                              char(10) ||
                              ?
        WHERE id = ?
    """, (
        summary,
        f"High-performing campaign (Score: {score.get('overall', 0)})",
        profile_id,
    ))

    return True
