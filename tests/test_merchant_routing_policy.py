import unittest

from payment_engine.gateway.merchant_policy import MerchantRoutingPolicy


class MerchantRoutingPolicyTests(unittest.TestCase):

    def setUp(self):
        self.policy = MerchantRoutingPolicy()

    def test_returns_default_when_no_policy_exists(self):
        self.assertIsNone(
            self.policy.get_gateway(
                "merchant-001",
                "NGN"
            )
        )

    def test_set_and_get_policy(self):
        self.policy.set_gateway(
            merchant_id="merchant-001",
            currency="NGN",
            gateway="flutterwave"
        )

        self.assertEqual(
            self.policy.get_gateway(
                "merchant-001",
                "NGN"
            ),
            "flutterwave"
        )

    def test_multiple_currencies(self):
        self.policy.set_gateway(
            "merchant-001",
            "USD",
            "stripe"
        )

        self.policy.set_gateway(
            "merchant-001",
            "USDT",
            "crypto"
        )

        self.assertEqual(
            self.policy.get_gateway(
                "merchant-001",
                "USD"
            ),
            "stripe"
        )

        self.assertEqual(
            self.policy.get_gateway(
                "merchant-001",
                "USDT"
            ),
            "crypto"
        )


if __name__ == "__main__":
    unittest.main()
