import unittest

from payment_engine.gateway.adaptive_engine import AdaptiveRoutingEngine
from payment_engine.gateway.metrics import GatewayMetrics
from payment_engine.gateway.health import GatewayHealthMonitor
from payment_engine.gateway.registry import GatewayRegistry


class AdaptiveRoutingEngineTests(unittest.TestCase):

    def setUp(self):
        self.registry = GatewayRegistry()
        self.health = GatewayHealthMonitor()
        self.metrics = GatewayMetrics()

        for gateway in (
            "paystack",
            "flutterwave",
            "stripe",
            "crypto",
        ):
            self.registry.register(gateway, object())
            self.health.set_status(gateway, "healthy")

        self.engine = AdaptiveRoutingEngine(
            registry=self.registry,
            health_monitor=self.health,
            metrics=self.metrics,
        )

    def test_ngn_prefers_paystack(self):
        self.assertEqual(
            self.engine.select_gateway({"currency": "NGN"}),
            "paystack"
        )

    def test_usd_prefers_stripe(self):
        self.assertEqual(
            self.engine.select_gateway({"currency": "USD"}),
            "stripe"
        )

    def test_crypto_prefers_crypto(self):
        self.assertEqual(
            self.engine.select_gateway({"currency": "USDT"}),
            "crypto"
        )

    def test_failover_when_primary_is_offline(self):
        self.health.set_status("paystack", "offline")

        self.assertEqual(
            self.engine.select_gateway({"currency": "NGN"}),
            "flutterwave"
        )


if __name__ == "__main__":
    unittest.main()
