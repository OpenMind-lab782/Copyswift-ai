import unittest
from unittest.mock import MagicMock

from payment_engine.repositories.postgres_payment_event_repository import (
    PostgreSQLPaymentEventRepository,
)


class PostgreSQLPaymentEventRepositoryTests(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.repository = PostgreSQLPaymentEventRepository(
            database=self.db
        )

    def test_save_event(self):
        event = {
            "event": "created",
            "status": "created",
            "timestamp": "2026-08-14 12:00:00",
            "metadata": {
                "source": "test"
            },
        }

        result = self.repository.save(
            "PAY-001",
            event,
        )

        self.assertEqual(result, event)
        self.db.engine.begin.assert_called_once()

    def test_list_events(self):
        connection = MagicMock()

        connection.execute.return_value.mappings.return_value.all.return_value = [
            {
                "id": 1,
                "reference": "PAY-001",
                "event": "created",
                "status": "created",
                "timestamp": "2026-08-14 12:00:00",
                "metadata": '{"source": "test"}',
            }
        ]

        self.db.connect.return_value.__enter__.return_value = connection

        events = self.repository.list("PAY-001")

        self.assertEqual(len(events), 1)
        self.assertEqual(
            events[0]["reference"],
            "PAY-001",
        )
        self.assertEqual(
            events[0]["event"],
            "created",
        )
        self.assertEqual(
            events[0]["metadata"]["source"],
            "test",
        )

    def test_clear(self):
        self.repository.clear()

        self.db.engine.begin.assert_called_once()


if __name__ == "__main__":
    unittest.main()
