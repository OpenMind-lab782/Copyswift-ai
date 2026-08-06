import unittest

from payment_engine.gateway.adaptive_engine import AdaptiveRoutingEngine
from payment_engine.gateway.capability_registry import GatewayCapabilityRegistry
from payment_engine.gateway.health import GatewayHealthMonitor
from payment_engine.gateway.metrics import GatewayMetrics
from payment_engine.gateway.merchant_policy import MerchantRoutingPolicy
from payment_engine.gateway.registry import GatewayRegistry


class CapabilityAwareRoutingTests(unittest.TestCase):

    def setUp(self):
        self.registry = GatewayRegistry()
        self.health = GatewayHealthMonitor()
        self.metrics = GatewayMetrics()
        self.policy = MerchantRoutingPolicy()
        self.capabilities = GatewayCapabilityRegistry()

        gateways = {
            "paystack": ["NGN"],
            "flutterwave": ["NGN", "USD"],
            "stripe": ["USD"],
            "crypto": ["USDT", "USDC"],
        }

        for gateway, currencies in gateways.items():
            self.registry.register(gateway, object())
            self.health.set_status(gateway, "healthy")
            self.capabilities.register(
                gateway,
                currencies=currencies,
            )

        self.engine = AdaptiveRoutingEngine(
            registry=self.registry,
            health_monitor=self.health,
            metrics=self.metrics,
            merchant_policy=self.policy,
            capability_registry=self.capabilities,
        )

    def test_currency_supported(self):
        self.assertEqual(
            self.engine.select_gateway({"currency": "USD"}),
            "stripe",
        )

    def test_invalid_override_is_ignored(self):
        self.policy.set_gateway(
            "merchant-001",
            "USD",
            "paystack",
        )

        self.assertEqual(
            self.engine.select_gateway({
                "merchant_id": "merchant-001",
                "currency": "USD",
            }),
            "stripe",
        )


if __name__ == "__main__":
    unittest.main()
