import unittest

from payment_engine.engine import PaymentEngine


class TestCorrelationIntegration(unittest.TestCase):

    def test_verify_payment_returns_correlation_id(self):
        engine = PaymentEngine()

        result = engine.verify_payment(
            "paystack",
            "CID-001",
        )

        self.assertIn("correlation_id", result)
        self.assertIsInstance(result["correlation_id"], str)


if __name__ == "__main__":
    unittest.main()
