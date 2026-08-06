"""
Swift Payment Engine Adapter
"""

from payment_engine.engine import PaymentEngine
from payment_engine.core.payment_history_service import PaymentHistoryService


class PaymentEngineAdapter:

    def __init__(self):
        self.engine = PaymentEngine()
        self.history = PaymentHistoryService()

    def execute(
        self,
        payment_request,
        gateway="paystack",
        customer_email="unknown@example.com",
    ):

        customer = {
            "reference": payment_request["reference"],
            "plan": payment_request["plan"],
        }

        result = self.engine.create_payment(
            gateway=gateway,
            amount=payment_request["amount"],
            currency=payment_request["currency"],
            customer=customer,
        )

        self.history.record(
            {
                "reference": result["reference"],
                "customer_email": customer_email,
                "gateway": result["gateway"],
                "amount": result["amount"],
                "currency": result["currency"],
                "status": result["status"],
            }
        )

        return {
            "reference": payment_request["reference"],
            "gateway": gateway,
            "engine_response": result,
        }
