"""
Checkout Session Builder
"""

from datetime import UTC, datetime
from uuid import uuid4


class CheckoutSessionBuilder:
    """
    Builds a checkout session for the selected plan.
    """

    PLAN_PRICES = {
        "Starter": 8,
        "Pro": 25,
        "Enterprise": None,
    }

    def create(self, recommendation):

        plan = recommendation["plan"]

        return {
            "session_id": str(uuid4()),
            "created_at": datetime.now(UTC).isoformat(),
            "plan": plan,
            "price_usd": self.PLAN_PRICES.get(plan),
            "payment_required": recommendation["payment_required"],
            "next_action": recommendation["action"],
        }
