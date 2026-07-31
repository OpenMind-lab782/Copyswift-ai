from payment_engine.database.database import SessionLocal
from payment_engine.database.repository import TransactionRepository


def main():
    db = SessionLocal()

    try:
        repo = TransactionRepository(db)

        # Create a test transaction
        transaction = repo.create(
            reference="TEST-001",
            gateway="paystack",
            amount=100.00,
            currency="USD",
            status="pending",
            customer_id="customer-001",
        )

        print("Created:", transaction.reference)

        # Retrieve it
        found = repo.get_by_reference("TEST-001")
        print("Retrieved:", found.reference, found.status)

        # Update status
        updated = repo.update_status("TEST-001", "verified")
        print("Updated:", updated.reference, updated.status)

        # List all transactions
        print("Total Transactions:", len(repo.list_all()))

    finally:
        db.close()


if __name__ == "__main__":
    main()
