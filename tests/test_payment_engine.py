import unittest

from payment_engine.engine import PaymentEngine
from payment_engine.models import PaymentRequest
from payment_engine.transaction import Transaction


class TestPaymentEngine(unittest.TestCase):

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
