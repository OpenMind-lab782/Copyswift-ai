from payment_engine.gateways.base import BaseGateway


class PaystackGateway(BaseGateway):
    """
    Development Mock Paystack Gateway.

    This adapter simulates successful Paystack behaviour
    until real merchant credentials are available.
    """

    @property
    def name(self):
        return "paystack"

    def initialize_payment(self, amount, currency, customer, **kwargs):
        return {
            "status": "verified",
            "gateway": self.name,
            "mode": "mock",
            "authorization_url": (
                f"https://mock.paystack.local/pay/{customer}"
            ),
            "reference": kwargs.get(
                "reference",
                f"MOCK-{customer}"
            ),
            "amount": amount,
            "currency": currency,
        }

    def verify_payment(self, reference):
        return {
            "status": "verified",
            "gateway": self.name,
            "mode": "mock",
            "reference": reference,
            "paid": True,
            "amount": 100,
            "currency": "NGN",
            "customer": "mock@copyswiftai.com",
            "message": "Mock payment verified successfully."
        }

    def refund_payment(self, reference, amount=None):
        return {
            "status": "success",
            "gateway": self.name,
            "mode": "mock",
            "reference": reference,
            "refunded_amount": amount,
            "message": "Mock refund completed."
        }

    def health_check(self):
        return {
            "status": "healthy",
            "gateway": self.name,
            "mode": "mock"
        }
