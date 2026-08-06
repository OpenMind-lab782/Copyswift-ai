import unittest

from payment_engine.gateway.flutterwave import FlutterwaveGateway


class FlutterwaveGatewayTests(unittest.TestCase):

    def setUp(self):
        self.gateway = FlutterwaveGateway()

    def test_gateway_is_adapter(self):
        self.assertTrue(
            hasattr(
                self.gateway,
                "initialize_payment"
            )
        )

    def test_initialize_payment(self):
        payment = {
            "reference": "FLW-001",
            "amount": 7500,
            "currency": "NGN"
        }

        result = self.gateway.initialize_payment(payment)

        self.assertEqual(
            result["reference"],
            "FLW-001"
        )

        self.assertEqual(
            result["status"],
            "initialized"
        )

    def test_verify_payment(self):
        result = self.gateway.verify_payment(
            "FLW-001"
        )

        self.assertEqual(
            result["reference"],
            "FLW-001"
        )

        self.assertEqual(
            result["status"],
            "verified"
        )

    def test_refund_payment(self):
        result = self.gateway.refund_payment(
            "FLW-001"
        )

        self.assertEqual(
            result["reference"],
            "FLW-001"
        )

        self.assertEqual(
            result["status"],
            "refunded"
        )


if __name__ == "__main__":
    unittest.main()
