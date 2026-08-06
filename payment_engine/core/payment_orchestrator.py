"""
Payment Orchestrator
"""


class PaymentOrchestrator:
    """
    Coordinates payment requests before handing them
    to the Swift Payment Engine.
    """

    def process(self, payment_request):

        return {
            "reference": payment_request["reference"],
            "status": "accepted",
            "amount": payment_request["amount"],
            "currency": payment_request["currency"],
            "plan": payment_request["plan"],
            "next_stage": "swift_payment_engine",
        }
