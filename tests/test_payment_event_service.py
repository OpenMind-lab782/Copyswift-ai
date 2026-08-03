import unittest

from payment_engine.services.payment_event_service import (
    payment_event_service,
)


class PaymentEventServiceTests(unittest.TestCase):

    def setUp(self):
        payment_event_service.clear()

    def test_record_and_list_events(self):
        payment_event_service.record(
            "PAY-001",
            "created",
            "created",
            "2026-08-03 10:00:00"
        )

        events = payment_event_service.list("PAY-001")

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "created")
        self.assertEqual(events[0]["status"], "created")


if __name__ == "__main__":
    unittest.main()
