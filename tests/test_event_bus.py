import unittest

from payment_engine.events import EventBus


class TestEventBus(unittest.TestCase):

    def setUp(self):
        self.bus = EventBus()
        self.received = []

    def listener(self, payload):
        self.received.append(payload)

    def test_publish_payment_verified(self):
        self.bus.subscribe("payment_verified", self.listener)

        self.bus.publish(
            "payment_verified",
            gateway="paystack",
            reference="REF-001",
            status="verified",
        )

        self.assertEqual(len(self.received), 1)
        self.assertEqual(
            self.received[0]["reference"],
            "REF-001"
        )
        self.assertEqual(
            self.received[0]["status"],
            "verified"
        )

    def test_clear_removes_subscribers(self):
        self.bus.subscribe("payment_verified", self.listener)

        self.bus.clear()

        self.bus.publish(
            "payment_verified",
            reference="REF-002"
        )

        self.assertEqual(len(self.received), 0)


if __name__ == "__main__":
    unittest.main()
