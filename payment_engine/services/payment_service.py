from payment_engine.repositories import payment_repository
from payment_engine.transactions import transaction_manager


class PaymentService:

    def save(self, payment):
        return transaction_manager.execute(
            payment_repository.save,
            payment
        )

    def get(self, reference):
        return payment_repository.get(reference)

    def list(self):
        return payment_repository.list()

    def find_by_idempotency_key(self, key):
        if not key:
            return None

        for payment in self.list():
            if payment.get("idempotency_key") == key:
                return payment

        return None

    def clear(self):
        return payment_repository.clear()

    def update_status(self, reference, status):
        return transaction_manager.execute(
            payment_repository.update_status,
            reference,
            status
        )
