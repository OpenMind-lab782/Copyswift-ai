import unittest

from payment_engine.engine import PaymentEngine


class TestPaymentEngineIntegration(unittest.TestCase):

    def setUp(self):
        self.engine = PaymentEngine()

    def test_verify_payment_success(self):
        result = self.engine.verify_payment(
            "paystack",
            "INTEGRATION-REF-001"
        )

        self.assertEqual(result.get("status"), "verified")

    def test_duplicate_reference(self):
        reference = "INTEGRATION-DUP-001"

        self.engine.verify_payment(
            "paystack",
            reference
        )

        second = self.engine.verify_payment(
            "paystack",
            reference
        )

        self.assertEqual(
            second.get("status"),
            "duplicate"
        )

    def test_multiple_providers(self):
        expected = {
            "paystack": "verified",
            "flutterwave": "failed",
        }

        for provider, status in expected.items():
            result = self.engine.verify_payment(
                provider,
                f"{provider}-001"
            )

            self.assertEqual(
                result.get("status"),
                status
            )


if __name__ == "__main__":
    unittest.main()
