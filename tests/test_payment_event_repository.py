import unittest

from payment_engine.repositories.payment_event_repository import (
    PaymentEventRepository,
)


class PaymentEventRepositoryTests(unittest.TestCase):

    def setUp(self):
        self.repository = PaymentEventRepository()

    def test_save_and_list_events(self):

        self.repository.save(
            "PAY-001",
            {
                "event": "created",
                "status": "created"
            }
        )

        events = self.repository.list("PAY-001")

        self.assertEqual(len(events), 1)

        self.assertEqual(
            events[0]["event"],
            "created"
        )


if __name__ == "__main__":
    unittest.main()
