import unittest

from payment_engine.engine import PaymentEngine


class TestPaymentEngineEvents(unittest.TestCase):

    def setUp(self):
        self.engine = PaymentEngine()
        self.received = []

        def listener(payload):
            self.received.append(payload)

        self.engine.events.subscribe(
            "payment_verified",
            listener
        )

    def test_payment_verified_event(self):
        self.engine.verify_payment(
            "paystack",
            "EVENT-001"
        )

        self.assertEqual(len(self.received), 1)
        self.assertEqual(
            self.received[0]["reference"],
            "EVENT-001"
        )
        self.assertEqual(
            self.received[0]["status"],
            "verified"
        )


if __name__ == "__main__":
    unittest.main()
