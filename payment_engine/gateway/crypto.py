from payment_engine.gateway.adapter import GatewayAdapter


class CryptoGateway(GatewayAdapter):
    """
    Mock crypto payment gateway.
    This implementation will later support
    USDT, USDC, BTC, ETH, TON, TRX, BNB and others.
    """

    def initialize_payment(self, payment):
        return {
            "reference": payment["reference"],
            "status": "initialized",
            "gateway": "crypto",
            "amount": payment.get("amount"),
            "currency": payment.get("currency"),
        }

    def verify_payment(self, reference):
        return {
            "reference": reference,
            "status": "verified",
            "gateway": "crypto",
        }

    def refund_payment(self, reference):
        return {
            "reference": reference,
            "status": "refunded",
            "gateway": "crypto",
        }
