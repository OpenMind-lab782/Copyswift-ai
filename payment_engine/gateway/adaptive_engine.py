from payment_engine.gateway.routing import SmartRoutingPolicy
from payment_engine.gateway.weighted_routing import WeightedRoutingStrategy


class AdaptiveRoutingEngine:
    """
    Merchant-aware, capability-aware adaptive routing engine.
    """

    FALLBACKS = {
        "paystack": ["flutterwave", "stripe", "crypto"],
        "flutterwave": ["paystack", "stripe", "crypto"],
        "stripe": ["paystack", "flutterwave", "crypto"],
        "crypto": ["stripe", "flutterwave", "paystack"],
    }

    def __init__(
        self,
        registry,
        health_monitor,
        metrics,
        merchant_policy=None,
        capability_registry=None,
    ):
        self.registry = registry
        self.health = health_monitor
        self.metrics = metrics
        self.merchant_policy = merchant_policy
        self.capability_registry = capability_registry

        self.policy = SmartRoutingPolicy()
        self.weighted = WeightedRoutingStrategy(metrics)

    def _supports_currency(self, gateway, currency):
        if self.capability_registry is None:
            return True

        capabilities = self.capability_registry.get(gateway)

        if capabilities is None:
            return True

        currencies = capabilities.get("currencies", [])

        return currency in currencies

    def _preferred_gateway(self, payment):
        merchant_id = payment.get("merchant_id")
        currency = (payment.get("currency") or "").upper()

        if self.merchant_policy is not None and merchant_id:
            gateway = self.merchant_policy.get_gateway(
                merchant_id,
                currency,
            )

            if (
                gateway is not None
                and self._supports_currency(gateway, currency)
            ):
                return gateway

        return self.policy.select_gateway(payment)

    def select_gateway(self, payment):
        currency = (payment.get("currency") or "").upper()

        preferred = self._preferred_gateway(payment)

        if (
            self.health.get_status(preferred) == "healthy"
            and self._supports_currency(preferred, currency)
        ):
            return preferred

        candidates = []

        for gateway in self.FALLBACKS.get(preferred, []):
            if (
                self.registry.get(gateway) is not None
                and self.health.get_status(gateway) == "healthy"
                and self._supports_currency(gateway, currency)
            ):
                candidates.append(gateway)

        return self.weighted.select(candidates)
