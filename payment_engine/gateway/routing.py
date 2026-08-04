class SmartRoutingPolicy:
    """
    Selects the most appropriate payment gateway
    based on payment attributes.
    """

    def select_gateway(self, payment):
        currency = (payment.get("currency") or "").upper()

        if currency == "NGN":
            return "paystack"

        if currency == "USD":
            return "stripe"

        if currency in ("USDT", "USDC"):
            return "crypto"

        return "flutterwave"
