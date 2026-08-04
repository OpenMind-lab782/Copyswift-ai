import unittest

from payment_engine.gateway.crypto import CryptoGateway


class CryptoGatewayTests(unittest.TestCase):

    def setUp(self):
        self.gateway = CryptoGateway()

    def test_gateway_is_adapter(self):
        self.assertTrue(
            hasattr(
                self.gateway,
                "initialize_payment"
            )
        )

    def test_initialize_payment(self):
        payment = {
            "reference": "CRYPTO-001",
            "amount": 50,
            "currency": "USDT"
        }

        result = self.gateway.initialize_payment(payment)

        self.assertEqual(
            result["reference"],
            "CRYPTO-001"
        )

        self.assertEqual(
            result["status"],
            "initialized"
        )

    def test_verify_payment(self):
        result = self.gateway.verify_payment(
            "CRYPTO-001"
        )

        self.assertEqual(
            result["reference"],
            "CRYPTO-001"
        )

        self.assertEqual(
            result["status"],
            "verified"
        )

    def test_refund_payment(self):
        result = self.gateway.refund_payment(
            "CRYPTO-001"
        )

        self.assertEqual(
            result["reference"],
            "CRYPTO-001"
        )

        self.assertEqual(
            result["status"],
            "refunded"
        )


if __name__ == "__main__":
    unittest.main()
