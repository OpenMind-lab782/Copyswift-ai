import os
import unittest

from payment_engine.database.sqlite import SQLiteDatabase
from payment_engine.repositories.sqlite_reconciliation_repository import (
    SQLiteReconciliationRepository,
)
from payment_engine.repositories.sqlite_reconciliation_report_repository import (
    SQLiteReconciliationReportRepository,
)
from payment_engine.repositories.sqlite_settlement_repository import (
    SQLiteSettlementRepository,
)


class Batch67PersistenceTests(unittest.TestCase):

    RECONCILIATION_DATABASE = "test_batch67_reconciliation.db"
    REPORT_DATABASE = "test_batch67_report.db"
    SETTLEMENT_DATABASE = "test_batch67_settlement.db"

    def tearDown(self):
        for database in (
            self.RECONCILIATION_DATABASE,
            self.REPORT_DATABASE,
            self.SETTLEMENT_DATABASE,
        ):
            if os.path.exists(database):
                os.remove(database)

    def test_reconciliation_survives_database_reopen(self):
        database = SQLiteDatabase(
            self.RECONCILIATION_DATABASE
        )

        repository = SQLiteReconciliationRepository(
            database
        )

        repository.save(
            "merchant-067",
            {
                "reference": "PAY-B67-001",
            },
        )

        database.close()

        reopened = SQLiteDatabase(
            self.RECONCILIATION_DATABASE
        )

        repository = SQLiteReconciliationRepository(
            reopened
        )

        records = repository.list(
            "merchant-067"
        )

        reopened.close()

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0]["reference"],
            "PAY-B67-001",
        )

    def test_report_survives_database_reopen(self):
        database = SQLiteDatabase(
            self.REPORT_DATABASE
        )

        repository = SQLiteReconciliationReportRepository(
            database
        )

        repository.save(
            "merchant-067",
            {
                "reference": "PAY-B67-002",
                "amount": 12500,
                "currency": "BWP",
            },
        )

        database.close()

        reopened = SQLiteDatabase(
            self.REPORT_DATABASE
        )

        repository = SQLiteReconciliationReportRepository(
            reopened
        )

        records = repository.list(
            "merchant-067"
        )

        reopened.close()

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0]["reference"],
            "PAY-B67-002",
        )
        self.assertEqual(
            records[0]["amount"],
            12500,
        )
        self.assertEqual(
            records[0]["currency"],
            "BWP",
        )

    def test_settlement_survives_database_reopen(self):
        database = SQLiteDatabase(
            self.SETTLEMENT_DATABASE
        )

        repository = SQLiteSettlementRepository(
            database
        )

        repository.save(
            "merchant-067",
            {
                "reference": "PAY-B67-003",
                "amount": 25000,
                "currency": "NGN",
            },
        )

        database.close()

        reopened = SQLiteDatabase(
            self.SETTLEMENT_DATABASE
        )

        repository = SQLiteSettlementRepository(
            reopened
        )

        settlements = repository.list(
            "merchant-067"
        )

        reopened.close()

        self.assertEqual(len(settlements), 1)
        self.assertEqual(
            settlements[0]["reference"],
            "PAY-B67-003",
        )
        self.assertEqual(
            settlements[0]["amount"],
            25000,
        )
        self.assertEqual(
            settlements[0]["currency"],
            "NGN",
        )


if __name__ == "__main__":
    unittest.main()
