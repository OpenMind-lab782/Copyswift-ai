import unittest

from payment_engine.engine import PaymentEngine
from payment_engine.services.payment_service import PaymentService


class TestPaymentEngineEvents(unittest.TestCase):

    def setUp(self):
        self.payment_service = PaymentService()
        self.payment_service.clear()
        self.payment_service.save({
            "reference": "EVENT-001",
            "merchant_id": "merchant-076",
            "amount": 100,
            "currency": "NGN",
            "status": "pending",
            "gateway": "paystack",
            "customer_email": "customer@example.com",
            "metadata": {},
            "idempotency_key": None,
        })

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
