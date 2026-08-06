"""
Payment Session Bridge
"""


class PaymentSessionBridge:
    """
    Converts a checkout session into a payment request
    understood by the Swift Payment Engine.
    """

    def create_payment(self, session):

        return {
            "reference": session["session_id"],
            "amount": session["price_usd"],
            "currency": "USD",
            "plan": session["plan"],
            "payment_required": session["payment_required"],
            "status": "pending",
        }
