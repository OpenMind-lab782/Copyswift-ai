import os
import unittest

from payment_engine.database.sqlite import SQLiteDatabase
from payment_engine.repositories.sqlite_reconciliation_repository import (
    SQLiteReconciliationRepository,
)


class SQLiteReconciliationRepositoryTests(unittest.TestCase):

    DATABASE = "test_reconciliation.db"

    def setUp(self):
        if os.path.exists(self.DATABASE):
            os.remove(self.DATABASE)

        self.database = SQLiteDatabase(self.DATABASE)
        self.repository = SQLiteReconciliationRepository(
            self.database
        )

    def tearDown(self):
        self.database.close()

        if os.path.exists(self.DATABASE):
            os.remove(self.DATABASE)

    def test_save_and_reload(self):

        self.repository.save(
            merchant_id="merchant-001",
            record={
                "reference": "PAY-001",
            },
        )

        self.database.close()

        reopened = SQLiteDatabase(self.DATABASE)

        repository = SQLiteReconciliationRepository(
            reopened
        )

        records = repository.list(
            "merchant-001"
        )

        reopened.close()

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0]["reference"],
            "PAY-001"
        )


if __name__ == "__main__":
    unittest.main()
