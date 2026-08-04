from payment_engine.gateway.adapter import GatewayAdapter


class PaystackGateway(GatewayAdapter):
    """
    Mock Paystack gateway implementation.
    This will later be connected to the real Paystack API.
    """

    def initialize_payment(self, payment):
        return {
            "reference": payment["reference"],
            "status": "initialized",
            "gateway": "paystack",
            "amount": payment.get("amount"),
            "currency": payment.get("currency"),
        }

    def verify_payment(self, reference):
        return {
            "reference": reference,
            "status": "verified",
            "gateway": "paystack",
        }

    def refund_payment(self, reference):
        return {
            "reference": reference,
            "status": "refunded",
            "gateway": "paystack",
        }
