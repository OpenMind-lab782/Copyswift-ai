import unittest

from payment_engine.gateway.failover import GatewayFailoverEngine
from payment_engine.gateway.registry import GatewayRegistry
from payment_engine.gateway.health import GatewayHealthMonitor


class GatewayFailoverTests(unittest.TestCase):

    def setUp(self):
        self.registry = GatewayRegistry()
        self.health = GatewayHealthMonitor()

        self.registry.register("paystack", object())
        self.registry.register("flutterwave", object())
        self.registry.register("stripe", object())

        self.engine = GatewayFailoverEngine(
            self.registry,
            self.health
        )

    def test_returns_requested_gateway_when_healthy(self):

        self.health.set_status(
            "paystack",
            "healthy"
        )

        self.assertEqual(
            self.engine.select("paystack"),
            "paystack"
        )

    def test_fails_over_when_gateway_unhealthy(self):

        self.health.set_status(
            "paystack",
            "offline"
        )

        self.health.set_status(
            "flutterwave",
            "healthy"
        )

        self.assertEqual(
            self.engine.select("paystack"),
            "flutterwave"
        )

    def test_returns_none_when_no_gateway_is_healthy(self):

        self.assertIsNone(
            self.engine.select("paystack")
        )


if __name__ == "__main__":
    unittest.main()
