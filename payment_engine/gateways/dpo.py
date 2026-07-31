from payment_engine.gateways.base import BaseGateway
from payment_engine.gateway_capabilities import GatewayCapabilities


class DPOGateway(BaseGateway):

    @property
    def name(self):
        return "dpo"

    @property
    def capabilities(self):
        return GatewayCapabilities(
            supports_cards=True,
            supports_bank_transfer=True,
        )

    def initialize_payment(self, amount, currency, customer, **kwargs):
        return {
            "status": "success",
            "gateway": self.name,
            "mode": "mock",
            "amount": amount,
            "currency": currency,
            "customer": customer,
        }

    def verify_payment(self, reference):
        return {
            "status": "verified",
            "gateway": self.name,
            "mode": "mock",
            "reference": reference,
            "paid": True,
        }

    def refund_payment(self, reference, amount=None):
        return {
            "status": "unsupported",
            "gateway": self.name,
            "reference": reference,
            "message": "Refunds are not supported.",
        }

    def health_check(self):
        return {
            "status": "healthy",
            "gateway": self.name,
            "mode": "mock",
        }
