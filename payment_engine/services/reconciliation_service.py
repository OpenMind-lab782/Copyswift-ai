class ReconciliationService:

    def __init__(self):
        self._records = {}

    def record(
        self,
        merchant_id,
        reference,
    ):
        record = {
            "merchant_id": merchant_id,
            "reference": reference,
        }

        self._records.setdefault(
            merchant_id,
            []
        ).append(record)

        return record

    def list(self, merchant_id):
        return list(
            self._records.get(
                merchant_id,
                []
            )
        )

    def clear(self):
        self._records.clear()


reconciliation_service = ReconciliationService()
