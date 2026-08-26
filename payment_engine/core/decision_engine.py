"""
AI Decision Engine
"""

from datetime import UTC, datetime


class DecisionEngine:
    """
    Converts strategist recommendations into standardized AI decisions.
    """

    def __init__(self, provider=None):
        self.provider = provider

    def decide(self, recommendation):
        confidence = recommendation.get("confidence", 0.0)

        if confidence >= 0.90:
            risk = "low"
        elif confidence >= 0.70:
            risk = "medium"
        else:
            risk = "high"

        return {
            "action": recommendation.get("action"),
            "confidence": confidence,
            "risk": risk,
            "reason": recommendation.get("reason"),
            "trend": recommendation.get("trend"),
            "generated_at": datetime.now(UTC).isoformat(),
        }
