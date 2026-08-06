import unittest

from payment_engine.gateway.registry import GatewayRegistry


class GatewayRegistryTests(unittest.TestCase):

    def setUp(self):
        self.registry = GatewayRegistry()

    def test_register_and_get_gateway(self):

        gateway = object()

        self.registry.register(
            "paystack",
            gateway
        )

        self.assertIs(
            self.registry.get("paystack"),
            gateway
        )

    def test_list_gateways(self):

        self.registry.register(
            "paystack",
            object()
        )

        self.registry.register(
            "flutterwave",
            object()
        )

        gateways = self.registry.list()

        self.assertEqual(
            sorted(gateways),
            ["flutterwave", "paystack"]
        )


if __name__ == "__main__":
    unittest.main()
