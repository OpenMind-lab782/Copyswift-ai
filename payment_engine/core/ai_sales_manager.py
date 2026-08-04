"""
AI Sales Manager
"""


class AISalesManager:
    """
    Generates basic sales guidance based on customer intent.
    """

    def assist(self, customer):
        intent = (customer.get("intent") or "").lower()

        if intent == "buy":
            message = "Guide the customer through the purchase process."

        elif intent == "learn":
            message = "Recommend educational resources and product benefits."

        else:
            message = "Engage the customer and identify their needs."

        return {
            "customer": customer.get("name", "Guest"),
            "intent": intent or "unknown",
            "message": message,
        }
