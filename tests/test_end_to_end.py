import unittest

from payment_engine.engine import PaymentEngine
from payment_engine.services.payment_service import PaymentService


class TestEndToEnd(unittest.TestCase):

    def test_engine_initializes(self):
        engine = PaymentEngine()
        self.assertIsNotNone(engine)

    def test_verify_duplicate_reference(self):
        payment_service = PaymentService()
        payment_service.clear()
        payment_service.save({
            "reference": "TEST-REFERENCE-001",
            "merchant_id": "merchant-076",
            "amount": 100,
            "currency": "NGN",
            "status": "pending",
            "gateway": "paystack",
            "customer_email": "customer@example.com",
            "metadata": {},
            "idempotency_key": None,
        })

        engine = PaymentEngine()

        reference = "TEST-REFERENCE-001"

        first = engine.verify_payment("paystack", reference)
        second = engine.verify_payment("paystack", reference)

        self.assertEqual(second.get("status"), "duplicate")


if __name__ == "__main__":
    unittest.main()
