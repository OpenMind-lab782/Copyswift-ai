from payment_engine.base import BaseGateway

class FlutterwaveGateway(BaseGateway):

    name = "flutterwave"

    def initialize_payment(self, amount, currency, customer):
        return {
            "success": True,
            "gateway": self.name,
            "amount": amount,
            "currency": currency
        }

    def verify_payment(self, reference):
        return {
            "success": False,
            "gateway": self.name,
            "status": "failed",
            "reference": reference,
            "verified": False,
        }

    def refund_payment(self, reference):
        return {"refunded": False}

    def handle_webhook(self, payload):
        return True
