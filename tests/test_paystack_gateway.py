import unittest

from payment_engine.gateway.paystack import PaystackGateway


class PaystackGatewayTests(unittest.TestCase):

    def setUp(self):
        self.gateway = PaystackGateway()

    def test_gateway_is_adapter(self):
        self.assertTrue(
            hasattr(
                self.gateway,
                "initialize_payment"
            )
        )

    def test_initialize_payment(self):
        payment = {
            "reference": "PAY-001",
            "amount": 5000,
            "currency": "NGN"
        }

        result = self.gateway.initialize_payment(payment)

        self.assertEqual(
            result["reference"],
            "PAY-001"
        )

        self.assertEqual(
            result["status"],
            "initialized"
        )

    def test_verify_payment(self):
        result = self.gateway.verify_payment(
            "PAY-001"
        )

        self.assertEqual(
            result["reference"],
            "PAY-001"
        )

        self.assertEqual(
            result["status"],
            "verified"
        )

    def test_refund_payment(self):
        result = self.gateway.refund_payment(
            "PAY-001"
        )

        self.assertEqual(
            result["reference"],
            "PAY-001"
        )

        self.assertEqual(
            result["status"],
            "refunded"
        )


if __name__ == "__main__":
    unittest.main()
