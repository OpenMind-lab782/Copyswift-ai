"""
Customer Journey Engine
"""


class CustomerJourneyEngine:
    """
    Builds a simple customer journey based on intent.
    """

    def journey(self, intent):

        intent = (intent or "").lower()

        if intent == "buy":
            return [
                "Discover CopySwiftAI",
                "Choose the right subscription",
                "Complete secure payment",
                "Start using AI tools",
            ]

        if intent == "learn":
            return [
                "Explore platform features",
                "Review AI capabilities",
                "Select a suitable plan",
            ]

        return [
            "Introduce CopySwiftAI",
            "Understand customer goals",
            "Recommend the next step",
        ]
