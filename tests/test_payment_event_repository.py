import os
import tempfile
import unittest

from payment_engine.database.sqlite import SQLiteDatabase
from payment_engine.repositories.sqlite_payment_event_repository import (
    SQLitePaymentEventRepository,
)


class PaymentEventRepositoryTests(unittest.TestCase):

    def setUp(self):
        fd, self.database_path = tempfile.mkstemp(
            prefix="batch75_event_repository_",
            suffix=".db",
        )
        os.close(fd)

        self.database = SQLiteDatabase(self.database_path)
        self.repository = SQLitePaymentEventRepository(
            self.database
        )

    def tearDown(self):
        self.database.close()

        if os.path.exists(self.database_path):
            os.remove(self.database_path)

    def test_save_and_list_events(self):
        self.repository.save(
            "PAY-001",
            {
                "event": "created",
                "status": "created",
            },
        )

        events = self.repository.list("PAY-001")

        self.assertEqual(len(events), 1)
        self.assertEqual(
            events[0]["event"],
            "created",
        )

    def test_has_verified_event_returns_false_when_absent(self):
        self.assertFalse(
            self.repository.has_verified_event("PAY-001")
        )

    def test_has_verified_event_returns_true_when_present(self):
        self.repository.save(
            "PAY-001",
            {
                "event": "verified",
                "status": "verified",
            },
        )

        self.assertTrue(
            self.repository.has_verified_event("PAY-001")
        )


if __name__ == "__main__":
    unittest.main()
