import unittest

from payment_engine.engine import PaymentEngine
from payment_engine.models import PaymentRequest
from payment_engine.transaction import Transaction


class TestPaymentEngine(unittest.TestCase):
    def test_gateway_capability_report(self):
        report = self.engine.gateway_capability_report()

        self.assertIn("crypto", report)
        self.assertIn("paystack", report)
        self.assertIn("flutterwave", report)
        self.assertIn("dpo", report)

        self.assertTrue(
            report["paystack"]["supports_refunds"]
        )

        self.assertTrue(
            report["flutterwave"]["supports_refunds"]
        )

        self.assertTrue(
            report["crypto"]["supports_crypto"]
        )

        self.assertIn(
            "supports_webhooks",
            report["paystack"]
        )

    def test_gateway_configuration_defaults_to_mock(self):
        self.assertEqual(
            self.engine.get_gateway_mode("paystack").value,
            "mock",
        )

    def test_gateway_webhook_contract_is_safe(self):
        gateway = self.engine.get_gateway("paystack")

        result = gateway.handle_webhook({
            "event": "test",
        })

        self.assertEqual(
            result["status"],
            "unsupported",
        )

        self.assertEqual(
            result["gateway"],
            "paystack",
        )


    def setUp(self):
        self.engine = PaymentEngine()

    def test_transaction_creation(self):
        tx = Transaction(
            gateway="crypto",
            amount=100,
            currency="USD",
            customer="test@example.com"
        )
        self.assertEqual(tx.status, "pending")

    def test_payment_request(self):
        req = PaymentRequest(
            gateway="crypto",
            amount=100,
            currency="USD",
            customer="test@example.com"
        )
        self.assertEqual(req.gateway, "crypto")

    def test_engine_exists(self):
        self.assertIsNotNone(self.engine)


if __name__ == "__main__":
    unittest.main()
