import unittest

from payment_engine.services.payment_event_service import (
    payment_event_service,
)


class PaymentEventMetadataTests(unittest.TestCase):

    def setUp(self):
        payment_event_service.clear()

    def test_event_supports_metadata(self):

        payment_event_service.record(
            reference="PAY-001",
            event="created",
            status="created",
            timestamp="2026-08-03 00:00:00",
            metadata={
                "gateway": "paystack",
                "amount": 5000,
            },
        )

        event = payment_event_service.list("PAY-001")[0]

        self.assertEqual(
            event["metadata"]["gateway"],
            "paystack",
        )

        self.assertEqual(
            event["metadata"]["amount"],
            5000,
        )


if __name__ == "__main__":
    unittest.main()
