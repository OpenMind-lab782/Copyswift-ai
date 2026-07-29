from payment_engine.gateways.base import BaseGateway


class PaystackGateway(BaseGateway):
    """
    Paystack Gateway Adapter
    """

    @property
    def name(self):
        return "paystack"

    def initialize_payment(self, amount, currency, customer, **kwargs):
        raise NotImplementedError(
            "Paystack initialize_payment() not yet implemented."
        )

    def verify_payment(self, reference):
        raise NotImplementedError(
            "Paystack verify_payment() not yet implemented."
        )

    def refund_payment(self, reference, amount=None):
        raise NotImplementedError(
            "Paystack refund_payment() not yet implemented."
        )

    def health_check(self):
        return {
            "status": "healthy",
            "gateway": self.name,
            "mode": "adapter-ready"
        }
