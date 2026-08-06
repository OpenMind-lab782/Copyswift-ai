import unittest

from payment_engine.gateway.stripe import StripeGateway


class StripeGatewayTests(unittest.TestCase):

    def setUp(self):
        self.gateway = StripeGateway()

    def test_gateway_is_adapter(self):
        self.assertTrue(
            hasattr(
                self.gateway,
                "initialize_payment"
            )
        )

    def test_initialize_payment(self):
        payment = {
            "reference": "STRIPE-001",
            "amount": 12000,
            "currency": "USD"
        }

        result = self.gateway.initialize_payment(payment)

        self.assertEqual(
            result["reference"],
            "STRIPE-001"
        )

        self.assertEqual(
            result["status"],
            "initialized"
        )

    def test_verify_payment(self):
        result = self.gateway.verify_payment(
            "STRIPE-001"
        )

        self.assertEqual(
            result["reference"],
            "STRIPE-001"
        )

        self.assertEqual(
            result["status"],
            "verified"
        )

    def test_refund_payment(self):
        result = self.gateway.refund_payment(
            "STRIPE-001"
        )

        self.assertEqual(
            result["reference"],
            "STRIPE-001"
        )

        self.assertEqual(
            result["status"],
            "refunded"
        )


if __name__ == "__main__":
    unittest.main()
