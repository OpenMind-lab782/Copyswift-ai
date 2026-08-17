import unittest

from sqlalchemy import create_engine

from payment_engine.database.postgres import PostgreSQLDatabase
from payment_engine.database.postgres_schema import initialize_postgres_schema
from payment_engine.repositories.postgres_payment_repository import (
    PostgreSQLPaymentRepository,
)


class PostgreSQLRepositoryTests(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            future=True,
        )

        self.database = PostgreSQLDatabase(
            database_url="sqlite:///:memory:",
            engine=self.engine,
        )

        # Schema provisioning is explicit.
        # Repository construction must not mutate the database schema.
        initialize_postgres_schema(self.database)

        self.repository = PostgreSQLPaymentRepository(
            database=self.database
        )

    def tearDown(self):
        self.database.dispose()

    def payment(self, **overrides):
        payment = {
            "reference": "PG-TEST-001",
            "merchant_id": "merchant-001",
            "amount": 125.50,
            "currency": "USD",
            "status": "pending",
            "gateway": "test",
            "customer_email": "customer@example.com",
            "metadata": {
                "source": "batch71c",
                "test": True,
            },
            "idempotency_key": "idem-001",
            "created_at": "2026-08-14 10:00:00",
            "updated_at": "2026-08-14 10:00:00",
        }

        payment.update(overrides)
        return payment

    def test_repository_exists(self):
        self.assertIsNotNone(self.repository)

    def test_save_and_get(self):
        payment = self.payment()

        result = self.repository.save(payment)

        self.assertEqual(
            result["reference"],
            "PG-TEST-001",
        )

        loaded = self.repository.get("PG-TEST-001")

        self.assertIsNotNone(loaded)
        self.assertEqual(
            loaded["reference"],
            "PG-TEST-001",
        )
        self.assertEqual(
            loaded["amount"],
            125.50,
        )
        self.assertEqual(
            loaded["currency"],
            "USD",
        )
        self.assertEqual(
            loaded["metadata"]["source"],
            "batch71c",
        )

    def test_get_unknown_reference_returns_none(self):
        self.assertIsNone(
            self.repository.get("UNKNOWN-REFERENCE")
        )

    def test_list_returns_persisted_payments(self):
        self.repository.save(
            self.payment(reference="PG-001")
        )

        self.repository.save(
            self.payment(reference="PG-002")
        )

        payments = self.repository.list()

        self.assertEqual(len(payments), 2)

        references = {
            payment["reference"]
            for payment in payments
        }

        self.assertEqual(
            references,
            {"PG-001", "PG-002"},
        )

    def test_update_status_persists_change(self):
        self.repository.save(self.payment())

        updated = self.repository.update_status(
            "PG-TEST-001",
            "completed",
        )

        self.assertIsNotNone(updated)
        self.assertEqual(
            updated["status"],
            "completed",
        )

        loaded = self.repository.get(
            "PG-TEST-001"
        )

        self.assertEqual(
            loaded["status"],
            "completed",
        )

    def test_update_unknown_reference_returns_none(self):
        result = self.repository.update_status(
            "UNKNOWN-REFERENCE",
            "completed",
        )

        self.assertIsNone(result)

    def test_clear_removes_all_payments(self):
        self.repository.save(
            self.payment(reference="PG-001")
        )

        self.repository.save(
            self.payment(reference="PG-002")
        )

        self.assertEqual(
            len(self.repository.list()),
            2,
        )

        self.repository.clear()

        self.assertEqual(
            self.repository.list(),
            [],
        )

    def test_save_same_reference_updates_existing_payment(self):
        self.repository.save(self.payment())

        updated_payment = self.payment(
            amount=999.99,
            status="completed",
        )

        self.repository.save(updated_payment)

        payments = self.repository.list()

        self.assertEqual(len(payments), 1)
        self.assertEqual(
            payments[0]["amount"],
            999.99,
        )
        self.assertEqual(
            payments[0]["status"],
            "completed",
        )

    def test_metadata_round_trip(self):
        payment = self.payment(
            metadata={
                "customer": {
                    "tier": "premium",
                },
                "items": [
                    "payment",
                    "engine",
                ],
                "verified": True,
            }
        )

        self.repository.save(payment)

        loaded = self.repository.get(
            "PG-TEST-001"
        )

        self.assertEqual(
            loaded["metadata"],
            payment["metadata"],
        )

    def test_idempotency_key_persists(self):
        self.repository.save(self.payment())

        loaded = self.repository.get(
            "PG-TEST-001"
        )

        self.assertEqual(
            loaded["idempotency_key"],
            "idem-001",
        )


if __name__ == "__main__":
    unittest.main()
