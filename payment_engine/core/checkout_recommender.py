"""
Checkout Recommendation Engine
"""


class CheckoutRecommender:
    """
    Recommends the next checkout action based on the selected plan.
    """

    def recommend(self, plan):

        plan = (plan or "").lower()

        recommendations = {
            "starter": {
                "plan": "Starter",
                "action": "Proceed to Starter checkout",
                "payment_required": True,
            },
            "pro": {
                "plan": "Pro",
                "action": "Proceed to Pro checkout",
                "payment_required": True,
            },
            "enterprise": {
                "plan": "Enterprise",
                "action": "Contact sales for Enterprise onboarding",
                "payment_required": False,
            },
        }

        return recommendations.get(
            plan,
            {
                "plan": "Unknown",
                "action": "Ask customer to choose a plan",
                "payment_required": False,
            },
        )
