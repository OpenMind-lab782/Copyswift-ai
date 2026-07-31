from payment_engine.gateways.base import BaseGateway
from payment_engine.gateway_capabilities import GatewayCapabilities
from payment_engine.utils.reference import PaymentReference


class PaystackGateway(BaseGateway):
    """
    Development Mock Paystack Gateway.

    This adapter simulates successful Paystack behaviour
    until real merchant credentials are available.
    """

    @property
    def name(self):
        return "paystack"


    @property
    def capabilities(self):
        return GatewayCapabilities(
            supports_cards=True,
            supports_bank_transfer=True,
            supports_refunds=True,
        )


    def initialize_payment(self, amount, currency, customer, **kwargs):
        reference = kwargs.get(
            "reference",
            PaymentReference.generate()
        )

        return {
            "status": "verified",
            "gateway": self.name,
            "mode": "mock",
            "authorization_url": (
                f"https://mock.paystack.local/pay/{reference}"
            ),
            "reference": reference,
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
