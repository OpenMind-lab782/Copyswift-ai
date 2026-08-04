"""
Market Strategist Core
"""


class MarketStrategist:
    """
    Converts Market Brain analysis into strategy recommendations.
    """

    def recommend(self, analysis):
        trend = analysis.get("trend", "unknown")
        confidence = analysis.get("confidence", 0.0)

        if trend == "bullish" and confidence >= 0.80:
            action = "buy"

        elif trend == "bearish" and confidence >= 0.80:
            action = "sell"

        else:
            action = "hold"

        return {
            "action": action,
            "confidence": confidence,
            "reason": analysis.get("summary", ""),
            "trend": trend,
        }
