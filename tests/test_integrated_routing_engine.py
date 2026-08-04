import unittest

from payment_engine.gateway.engine import RoutingEngine
from payment_engine.gateway.registry import GatewayRegistry
from payment_engine.gateway.health import GatewayHealthMonitor


class RoutingEngineTests(unittest.TestCase):

    def setUp(self):
        self.registry = GatewayRegistry()

        self.registry.register("paystack", object())
        self.registry.register("flutterwave", object())
        self.registry.register("stripe", object())
        self.registry.register("crypto", object())

        self.health = GatewayHealthMonitor()

        self.engine = RoutingEngine(
            registry=self.registry,
            health_monitor=self.health
        )

    def test_ngn_routes_to_paystack(self):

        self.health.set_status("paystack", "healthy")

        payment = {"currency": "NGN"}

        self.assertEqual(
            self.engine.select_gateway(payment),
            "paystack"
        )

    def test_failover_to_flutterwave(self):

        self.health.set_status("paystack", "offline")
        self.health.set_status("flutterwave", "healthy")

        payment = {"currency": "NGN"}

        self.assertEqual(
            self.engine.select_gateway(payment),
            "flutterwave"
        )

    def test_usd_routes_to_stripe(self):

        self.health.set_status("stripe", "healthy")

        payment = {"currency": "USD"}

        self.assertEqual(
            self.engine.select_gateway(payment),
            "stripe"
        )

    def test_crypto_routes(self):

        self.health.set_status("crypto", "healthy")

        payment = {"currency": "USDT"}

        self.assertEqual(
            self.engine.select_gateway(payment),
            "crypto"
        )


if __name__ == "__main__":
    unittest.main()
