from payment_engine.gateways.base import BaseGateway


class MockGateway(BaseGateway):
    """
    Mock payment gateway for development and testing.
    """

    @property
    def name(self):
        return "mock"

    def initialize_payment(self, amount, currency, customer, **kwargs):
        return {
            "status": "success",
            "gateway": self.name,
            "payment_url": "https://mock.swiftpayment.local/pay",
            "reference": kwargs.get("reference", "MOCK-TEST-001"),
            "amount": amount,
            "currency": currency,
            "customer": customer,
        }

    def verify_payment(self, reference):
        return {
            "status": "success",
            "verified": True,
            "gateway": self.name,
            "reference": reference,
            "amount": 100,
            "currency": "USD",
        }

    def refund_payment(self, reference, amount=None):
        return {
            "status": "success",
            "gateway": self.name,
            "reference": reference,
            "refunded_amount": amount,
        }

    def health_check(self):
        return {
            "status": "healthy",
            "gateway": self.name,
        }
