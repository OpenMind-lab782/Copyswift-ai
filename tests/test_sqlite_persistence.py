import os

from tests.base import SwiftEngineTestCase
from payment_engine.database.sqlite import SQLiteDatabase
from payment_engine.repositories.sqlite_payment_repository import SQLitePaymentRepository
from tests.support.factories import PaymentFactory


class SQLitePersistenceVerificationTests(SwiftEngineTestCase):

    DATABASE = "test_persistence.db"

    def setUp(self):
        if os.path.exists(self.DATABASE):
            os.remove(self.DATABASE)

        self.database = SQLiteDatabase(self.DATABASE)
        self.repository = SQLitePaymentRepository(self.database)

    def tearDown(self):
        self.database.close()

        if os.path.exists(self.DATABASE):
            os.remove(self.DATABASE)

    def test_payment_survives_database_reconnect(self):

        payment = PaymentFactory.create()

        self.repository.save(payment)

        reference = payment["reference"]

        self.database.close()

        reopened = SQLiteDatabase(self.DATABASE)
        repository = SQLitePaymentRepository(reopened)

        loaded = repository.get(reference)

        reopened.close()

        self.assertIsNotNone(loaded)
        self.assertEqual(
            loaded["reference"],
            reference
        )


if __name__ == "__main__":
    import unittest
    unittest.main()
