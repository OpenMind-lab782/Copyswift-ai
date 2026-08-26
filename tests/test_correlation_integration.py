import unittest

from payment_engine.engine import PaymentEngine
from payment_engine.services.payment_service import PaymentService


class TestCorrelationIntegration(unittest.TestCase):

    def test_verify_payment_returns_correlation_id(self):
        payment_service = PaymentService()
        payment_service.clear()
        payment_service.save({
            "reference": "CID-001",
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

        result = engine.verify_payment(
            "paystack",
            "CID-001",
        )

        self.assertIn("correlation_id", result)
        self.assertIsInstance(result["correlation_id"], str)


if __name__ == "__main__":
    unittest.main()
