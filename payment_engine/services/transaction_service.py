from payment_engine.database.database import get_db
from payment_engine.database.repository import TransactionRepository


class TransactionService:
    def __init__(self):
        self.db = get_db()
        self.repository = TransactionRepository(self.db)

    def statistics(self):
        records = self.repository.list_transactions()

        total = len(records)
        successful = sum(
            1 for r in records
            if (getattr(r, "status", "") or "").lower() == "success"
        )
        failed = sum(
            1 for r in records
            if (getattr(r, "status", "") or "").lower() == "failed"
        )
        pending = sum(
            1 for r in records
            if (getattr(r, "status", "") or "").lower() == "pending"
        )

        return {
            "total_transactions": total,
            "successful_transactions": successful,
            "failed_transactions": failed,
            "pending_transactions": pending,
        }
