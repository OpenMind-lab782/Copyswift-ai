from payment_engine.base import BaseGateway

class CryptoGateway(BaseGateway):

    name = "crypto"

    def initialize_payment(self, amount, currency, customer):
        return {
            "success": True,
            "gateway": self.name,
            "amount": amount,
            "currency": currency
        }

    def verify_payment(self, reference):
        return {"verified": False}

    def refund_payment(self, reference):
        return {"refunded": False}

    def handle_webhook(self, payload):
        return True
