from payment_engine.factory import RepositoryFactory


class ReconciliationService:

    def __init__(self, repository=None):
        self.repository = repository or RepositoryFactory.reconciliation_repository()

    def record(
        self,
        merchant_id,
        reference,
    ):
        record = {
            "merchant_id": merchant_id,
            "reference": reference,
        }

        return self.repository.save(
            merchant_id,
            record,
        )

    def list(self, merchant_id):
        return self.repository.list(
            merchant_id
        )

    def clear(self):
        self.repository.clear()


reconciliation_service = ReconciliationService()
