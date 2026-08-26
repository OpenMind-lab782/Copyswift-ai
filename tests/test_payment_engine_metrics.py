import unittest

from payment_engine.engine import PaymentEngine
from payment_engine.services.payment_service import PaymentService


class TestPaymentEngineMetrics(unittest.TestCase):

    def test_verify_request_metric(self):
        payment_service = PaymentService()
        payment_service.clear()
        payment_service.save({
            "reference": "METRIC-001",
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

        engine.verify_payment("paystack", "METRIC-001")

        metrics = engine.get_metrics()

        self.assertEqual(metrics.get("verify_requests"), 1)

    def test_verify_success_metric(self):
        payment_service = PaymentService()
        payment_service.clear()
        payment_service.save({
            "reference": "METRIC-002",
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

        engine.verify_payment("paystack", "METRIC-002")

        metrics = engine.get_metrics()

        self.assertEqual(metrics.get("verify_success"), 1)


if __name__ == "__main__":
    unittest.main()
