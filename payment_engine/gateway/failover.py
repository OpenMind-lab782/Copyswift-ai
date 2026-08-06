class GatewayFailoverEngine:
    """
    Selects an alternative payment gateway when the
    requested gateway is unavailable.
    """

    def __init__(self, registry, health_monitor):
        self.registry = registry
        self.health = health_monitor

    def select(self, preferred_gateway):
        # Use the preferred gateway if it is healthy.
        if self.health.get_status(preferred_gateway) == "healthy":
            return preferred_gateway

        # Otherwise, choose the first healthy gateway.
        for gateway in self.registry.list():
            if self.health.get_status(gateway) == "healthy":
                return gateway

        return None
