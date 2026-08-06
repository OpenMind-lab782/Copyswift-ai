from payment_engine.gateway.adapter import GatewayAdapter


class StripeGateway(GatewayAdapter):
    """
    Mock Stripe gateway implementation.
    This will later be connected to the real Stripe API.
    """

    def initialize_payment(self, payment):
        return {
            "reference": payment["reference"],
            "status": "initialized",
            "gateway": "stripe",
            "amount": payment.get("amount"),
            "currency": payment.get("currency"),
        }

    def verify_payment(self, reference):
        return {
            "reference": reference,
            "status": "verified",
            "gateway": "stripe",
        }

    def refund_payment(self, reference):
        return {
            "reference": reference,
            "status": "refunded",
            "gateway": "stripe",
        }
