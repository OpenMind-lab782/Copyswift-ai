import unittest

from payment_engine.gateway.routing import SmartRoutingPolicy


class SmartRoutingPolicyTests(unittest.TestCase):

    def setUp(self):
        self.policy = SmartRoutingPolicy()

    def test_ngn_routes_to_paystack(self):
        self.assertEqual(
            self.policy.select_gateway({"currency": "NGN"}),
            "paystack"
        )

    def test_usd_routes_to_stripe(self):
        self.assertEqual(
            self.policy.select_gateway({"currency": "USD"}),
            "stripe"
        )

    def test_usdt_routes_to_crypto(self):
        self.assertEqual(
            self.policy.select_gateway({"currency": "USDT"}),
            "crypto"
        )

    def test_usdc_routes_to_crypto(self):
        self.assertEqual(
            self.policy.select_gateway({"currency": "USDC"}),
            "crypto"
        )

    def test_unknown_currency_routes_to_flutterwave(self):
        self.assertEqual(
            self.policy.select_gateway({"currency": "KES"}),
            "flutterwave"
        )


if __name__ == "__main__":
    unittest.main()
