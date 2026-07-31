import unittest

from payment_engine.engine import PaymentEngine


class TestPaymentEngineMetrics(unittest.TestCase):

    def test_verify_request_metric(self):
        engine = PaymentEngine()

        engine.verify_payment("paystack", "METRIC-001")

        metrics = engine.get_metrics()

        self.assertEqual(metrics.get("verify_requests"), 1)

    def test_verify_success_metric(self):
        engine = PaymentEngine()

        engine.verify_payment("paystack", "METRIC-002")

        metrics = engine.get_metrics()

        self.assertEqual(metrics.get("verify_success"), 1)


if __name__ == "__main__":
    unittest.main()
