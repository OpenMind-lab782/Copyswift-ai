class SettlementRepository:

    def __init__(self):
        self._settlements = {}

    def save(self, merchant_id, settlement):

        self._settlements.setdefault(
            merchant_id,
            []
        ).append(settlement)

        return settlement

    def list(self, merchant_id):

        return list(
            self._settlements.get(
                merchant_id,
                []
            )
        )

    def clear(self):

        self._settlements.clear()
