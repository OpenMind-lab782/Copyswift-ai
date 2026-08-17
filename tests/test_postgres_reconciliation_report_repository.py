import unittest

from sqlalchemy import create_engine

from payment_engine.database.postgres import PostgreSQLDatabase
from payment_engine.database.postgres_schema import (
    initialize_postgres_schema,
)
from payment_engine.repositories.postgres_reconciliation_report_repository import (
    PostgreSQLReconciliationReportRepository,
)


class PostgreSQLReconciliationReportRepositoryTests(unittest.TestCase):

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

        self.repository = PostgreSQLReconciliationReportRepository(
            database=self.database
        )

    def tearDown(self):
        self.database.dispose()

    def test_save_and_list(self):
        record = {
            "reference": "PAY-REPORT-001",
            "amount": 12500,
            "currency": "BWP",
        }

        result = self.repository.save(
            "merchant-001",
            record,
        )

        self.assertEqual(result, record)

        rows = self.repository.list("merchant-001")

        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0]["reference"],
            "PAY-REPORT-001",
        )
        self.assertEqual(
            rows[0]["amount"],
            12500,
        )
        self.assertEqual(
            rows[0]["currency"],
            "BWP",
        )

    def test_list_is_merchant_scoped(self):
        self.repository.save(
            "merchant-001",
            {
                "reference": "PAY-REPORT-001",
                "amount": 12500,
                "currency": "BWP",
            },
        )

        self.repository.save(
            "merchant-002",
            {
                "reference": "PAY-REPORT-002",
                "amount": 9000,
                "currency": "BWP",
            },
        )

        rows = self.repository.list("merchant-001")

        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0]["reference"],
            "PAY-REPORT-001",
        )

    def test_clear(self):
        self.repository.save(
            "merchant-001",
            {
                "reference": "PAY-REPORT-001",
                "amount": 12500,
                "currency": "BWP",
            },
        )

        self.repository.clear()

        self.assertEqual(
            self.repository.list("merchant-001"),
            [],
        )


if __name__ == "__main__":
    unittest.main()
