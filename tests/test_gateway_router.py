import unittest

from payment_engine.gateway.registry import GatewayRegistry
from payment_engine.gateway.router import GatewayRouter


class GatewayRouterTests(unittest.TestCase):

    def setUp(self):
        self.registry = GatewayRegistry()

        self.paystack = object()
        self.crypto = object()

        self.registry.register(
            "paystack",
            self.paystack
        )

        self.registry.register(
            "crypto",
            self.crypto
        )

        self.router = GatewayRouter(
            self.registry
        )

    def test_route_existing_gateway(self):

        gateway = self.router.route(
            "paystack"
        )

        self.assertIs(
            gateway,
            self.paystack
        )

    def test_unknown_gateway_returns_none(self):

        self.assertIsNone(
            self.router.route(
                "unknown"
            )
        )


if __name__ == "__main__":
    unittest.main()
