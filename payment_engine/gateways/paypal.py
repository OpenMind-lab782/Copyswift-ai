from payment_engine.gateways.base import BaseGateway

class PayPalGateway(BaseGateway):

    @property
    def name(self):
        return "paypal"

    def initialize_payment(self, amount, currency, customer, **kwargs):
        raise NotImplementedError()

    def verify_payment(self, reference):
        raise NotImplementedError()

    def refund_payment(self, reference, amount=None):
        raise NotImplementedError()

    def health_check(self):
        return {
            "status": "healthy",
            "gateway": self.name,
            "mode": "adapter-ready"
        }
