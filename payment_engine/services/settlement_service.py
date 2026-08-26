from payment_engine.factory import RepositoryFactory


class SettlementService:

    def __init__(self, repository=None):
        self.repository = repository or RepositoryFactory.settlement_repository()

    def record(
        self,
        merchant_id,
        reference,
        amount,
        currency,
    ):
        settlement = {
            "merchant_id": merchant_id,
            "reference": reference,
            "amount": amount,
            "currency": currency,
        }

        return self.repository.save(
            merchant_id,
            settlement,
        )

    def list(self, merchant_id):
        return self.repository.list(
            merchant_id
        )

    def clear(self):
        self.repository.clear()


settlement_service = SettlementService()
