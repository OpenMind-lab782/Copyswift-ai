import unittest

from payment_engine.gateway.adaptive_engine import AdaptiveRoutingEngine
from payment_engine.gateway.health import GatewayHealthMonitor
from payment_engine.gateway.metrics import GatewayMetrics
from payment_engine.gateway.merchant_policy import MerchantRoutingPolicy
from payment_engine.gateway.registry import GatewayRegistry


class MerchantAdaptiveRoutingEngineTests(unittest.TestCase):

    def setUp(self):
        self.registry = GatewayRegistry()
        self.health = GatewayHealthMonitor()
        self.metrics = GatewayMetrics()
        self.policy = MerchantRoutingPolicy()

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
            merchant_policy=self.policy,
        )

    def test_merchant_override(self):
        self.policy.set_gateway(
            "merchant-001",
            "NGN",
            "flutterwave"
        )

        payment = {
            "merchant_id": "merchant-001",
            "currency": "NGN",
        }

        self.assertEqual(
            self.engine.select_gateway(payment),
            "flutterwave"
        )

    def test_default_policy_when_no_override(self):
        payment = {
            "merchant_id": "merchant-002",
            "currency": "USD",
        }

        self.assertEqual(
            self.engine.select_gateway(payment),
            "stripe"
        )


if __name__ == "__main__":
    unittest.main()
