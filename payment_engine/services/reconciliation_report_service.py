from payment_engine.factory import RepositoryFactory


class ReconciliationReportService:

    def __init__(self, repository=None):
        self.repository = (
            repository
            or RepositoryFactory.reconciliation_report_repository()
        )

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

        return self.repository.save(
            merchant_id,
            record,
        )

    def generate(self, merchant_id):

        records = self.repository.list(
            merchant_id
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
        self.repository.clear()


reconciliation_report_service = ReconciliationReportService()
