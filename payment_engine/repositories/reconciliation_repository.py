class ReconciliationRepository:

    def __init__(self):
        self._records = {}

    def save(self, merchant_id, record):

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
