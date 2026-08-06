import os

from tests.base import SwiftEngineTestCase
from payment_engine.database.sqlite import SQLiteDatabase


class SQLitePersistenceTests(SwiftEngineTestCase):

    def setUp(self):
        self.database_name = "test_swift_payment.db"

        if os.path.exists(self.database_name):
            os.remove(self.database_name)

        self.db = SQLiteDatabase(self.database_name)

    def tearDown(self):
        self.db.close()

        if os.path.exists(self.database_name):
            os.remove(self.database_name)

    def test_database_created(self):
        self.assertTrue(
            os.path.exists(self.database_name)
        )

    def test_payments_table_exists(self):
        cursor = self.db.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name='payments'
        """)

        self.assertIsNotNone(cursor.fetchone())


if __name__ == "__main__":
    import unittest
    unittest.main()
