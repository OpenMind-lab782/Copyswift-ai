import unittest

from payment_engine.gateway.capability_registry import (
    GatewayCapabilityRegistry,
)


class GatewayCapabilityRegistryTests(unittest.TestCase):

    def setUp(self):
        self.registry = GatewayCapabilityRegistry()

    def test_register_capabilities(self):
        self.registry.register(
            "paystack",
            currencies=["NGN", "USD"],
            refunds=True,
            recurring=False,
            settlement=True,
        )

        caps = self.registry.get("paystack")

        self.assertEqual(
            caps["currencies"],
            ["NGN", "USD"],
        )

        self.assertTrue(caps["refunds"])
        self.assertFalse(caps["recurring"])
        self.assertTrue(caps["settlement"])

    def test_unknown_gateway_returns_none(self):
        self.assertIsNone(
            self.registry.get("stripe")
        )

    def test_list_registered_gateways(self):
        self.registry.register(
            "paystack",
            currencies=["NGN"],
        )

        self.registry.register(
            "stripe",
            currencies=["USD"],
        )

        self.assertEqual(
            sorted(self.registry.list()),
            ["paystack", "stripe"],
        )


if __name__ == "__main__":
    unittest.main()
