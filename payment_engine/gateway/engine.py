from payment_engine.gateway.routing import SmartRoutingPolicy
from payment_engine.gateway.failover import GatewayFailoverEngine


class RoutingEngine:
    """
    Coordinates gateway selection using routing policy,
    health monitoring, and automatic failover.
    """

    def __init__(self, registry, health_monitor):
        self.registry = registry
        self.health_monitor = health_monitor
        self.routing_policy = SmartRoutingPolicy()
        self.failover = GatewayFailoverEngine(
            registry,
            health_monitor
        )

    def select_gateway(self, payment):
        preferred = self.routing_policy.select_gateway(payment)
        return self.failover.select(preferred)
