import os
import unittest

from payment_engine.database.sqlite import SQLiteDatabase
from payment_engine.repositories.sqlite_settlement_repository import (
    SQLiteSettlementRepository,
)


class SQLiteSettlementRepositoryTests(unittest.TestCase):

    DATABASE = "test_settlement.db"

    def setUp(self):
        if os.path.exists(self.DATABASE):
            os.remove(self.DATABASE)

        self.database = SQLiteDatabase(self.DATABASE)
        self.repository = SQLiteSettlementRepository(
            self.database
        )

    def tearDown(self):
        self.database.close()

        if os.path.exists(self.DATABASE):
            os.remove(self.DATABASE)

    def test_save_and_reload(self):

        self.repository.save(
            merchant_id="merchant-001",
            settlement={
                "reference": "PAY-001",
                "amount": 5000,
                "currency": "NGN",
            },
        )

        self.database.close()

        reopened = SQLiteDatabase(self.DATABASE)

        repository = SQLiteSettlementRepository(
            reopened
        )

        settlements = repository.list(
            "merchant-001"
        )

        reopened.close()

        self.assertEqual(
            len(settlements),
            1
        )

        self.assertEqual(
            settlements[0]["reference"],
            "PAY-001"
        )


if __name__ == "__main__":
    unittest.main()
