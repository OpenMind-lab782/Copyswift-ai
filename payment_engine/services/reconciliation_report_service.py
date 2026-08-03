class ReconciliationReportService:

    def __init__(self):
        self._records = {}

    def record(
        self,
        merchant_id,
        reference,
        amount,
        currency,
    ):
        record = {
            "reference": reference,
            "amount": amount,
            "currency": currency,
        }

        self._records.setdefault(
            merchant_id,
            []
        ).append(record)

        return record

    def generate(self, merchant_id):

        records = self._records.get(
            merchant_id,
            []
        )

        return {
            "merchant_id": merchant_id,
            "total_transactions": len(records),
            "total_amount": sum(
                item["amount"]
                for item in records
            ),
            "transactions": list(records),
        }

    def clear(self):
        self._records.clear()


reconciliation_report_service = ReconciliationReportService()
