from payment_engine.gateway.adapter import GatewayAdapter


class FlutterwaveGateway(GatewayAdapter):
    """
    Mock Flutterwave gateway implementation.
    This will later be connected to the real Flutterwave API.
    """

    def initialize_payment(self, payment):
        return {
            "reference": payment["reference"],
            "status": "initialized",
            "gateway": "flutterwave",
            "amount": payment.get("amount"),
            "currency": payment.get("currency"),
        }

    def verify_payment(self, reference):
        return {
            "reference": reference,
            "status": "verified",
            "gateway": "flutterwave",
        }

    def refund_payment(self, reference):
        return {
            "reference": reference,
            "status": "refunded",
            "gateway": "flutterwave",
        }
