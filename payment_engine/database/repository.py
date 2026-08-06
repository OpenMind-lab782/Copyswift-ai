from sqlalchemy.orm import Session

from .models import Transaction


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        reference: str,
        gateway: str,
        amount: float,
        currency: str = "USD",
        status: str = "pending",
        customer_id: str = None,
    ):
        transaction = Transaction(
            reference=reference,
            gateway=gateway,
            amount=amount,
            currency=currency,
            status=status,
            customer_id=customer_id,
        )

        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def get_by_reference(self, reference: str):
        return (
            self.db.query(Transaction)
            .filter(Transaction.reference == reference)
            .first()
        )

    def update_status(
        self,
        reference: str,
        status: str,
    ):
        transaction = self.get_by_reference(reference)

        if transaction:
            transaction.status = status
            self.db.commit()
            self.db.refresh(transaction)

        return transaction

    def list_all(self):
        return (
            self.db.query(Transaction)
            .order_by(Transaction.id.desc())
            .all()
        )

    def delete(self, reference: str):
        transaction = self.get_by_reference(reference)

        if transaction:
            self.db.delete(transaction)
            self.db.commit()

        return transaction
