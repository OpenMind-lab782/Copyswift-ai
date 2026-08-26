import unittest

from sqlalchemy import create_engine

from payment_engine.database.postgres import PostgreSQLDatabase
from payment_engine.database.postgres_schema import (
    initialize_postgres_schema,
)
from payment_engine.repositories.postgres_settlement_repository import (
    PostgreSQLSettlementRepository,
)


class PostgreSQLSettlementRepositoryTests(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            future=True,
        )

        self.database = PostgreSQLDatabase(
            database_url="sqlite:///:memory:",
            engine=self.engine,
        )

        initialize_postgres_schema(self.database)

        self.repository = PostgreSQLSettlementRepository(
            database=self.database
        )

    def tearDown(self):
        self.database.dispose()

    def test_save_and_list(self):
        settlement = {
            "reference": "SETTLE-001",
            "amount": 5000,
            "currency": "NGN",
        }

        result = self.repository.save(
            "merchant-001",
            settlement,
        )

        self.assertEqual(result, settlement)

        rows = self.repository.list("merchant-001")

        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0]["merchant_id"],
            "merchant-001",
        )
        self.assertEqual(
            rows[0]["reference"],
            "SETTLE-001",
        )
        self.assertEqual(
            rows[0]["amount"],
            5000,
        )
        self.assertEqual(
            rows[0]["currency"],
            "NGN",
        )

    def test_list_is_merchant_scoped(self):
        self.repository.save(
            "merchant-001",
            {
                "reference": "SETTLE-001",
                "amount": 5000,
                "currency": "NGN",
            },
        )

        self.repository.save(
            "merchant-002",
            {
                "reference": "SETTLE-002",
                "amount": 7000,
                "currency": "NGN",
            },
        )

        rows = self.repository.list("merchant-001")

        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0]["reference"],
            "SETTLE-001",
        )

    def test_clear(self):
        self.repository.save(
            "merchant-001",
            {
                "reference": "SETTLE-001",
                "amount": 5000,
                "currency": "NGN",
            },
        )

        self.repository.clear()

        self.assertEqual(
            self.repository.list("merchant-001"),
            [],
        )


if __name__ == "__main__":
    unittest.main()
