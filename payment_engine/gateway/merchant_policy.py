class MerchantRoutingPolicy:
    """
    Stores merchant-specific gateway preferences.

    Preferences are stored per merchant and currency.
    """

    def __init__(self):
        self._policies = {}

    def set_gateway(self, merchant_id, currency, gateway):
        currency = currency.upper()

        self._policies.setdefault(
            merchant_id,
            {}
        )[currency] = gateway

    def get_gateway(self, merchant_id, currency):
        currency = currency.upper()

        return (
            self._policies
            .get(merchant_id, {})
            .get(currency)
        )

    def clear(self):
        self._policies.clear()
