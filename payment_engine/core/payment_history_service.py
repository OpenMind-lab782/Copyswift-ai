"""
Payment History Service
"""

from payment_engine.core.payment_history_repository import (
    PaymentHistoryRepository,
)


class PaymentHistoryService:

    def __init__(self):
        self.repository = PaymentHistoryRepository()

    def record(self, payment):

        self.repository.save(
            reference=payment["reference"],
            customer_email=payment["customer_email"],
            gateway=payment["gateway"],
            amount=payment["amount"],
            currency=payment["currency"],
            status=payment["status"],
        )

    def history(self):
        return self.repository.all()
