from payment_engine.provider_mode import ProviderMode


class GatewaySelector:
    """
    Selects the most suitable gateway based on configuration.
    """

    def __init__(self, registry, gateway_config):
        self.registry = registry
        self.gateway_config = gateway_config

    def available_gateways(self):
        return self.registry.list()

    def live_gateways(self):
        return [
            gateway
            for gateway in self.registry.list()
            if self.gateway_config.mode(gateway) == ProviderMode.LIVE
        ]

    def sandbox_gateways(self):
        return [
            gateway
            for gateway in self.registry.list()
            if self.gateway_config.mode(gateway) == ProviderMode.SANDBOX
        ]

    def mock_gateways(self):
        return [
            gateway
            for gateway in self.registry.list()
            if self.gateway_config.mode(gateway) == ProviderMode.MOCK
        ]


    def gateways_supporting(self, capability):
        """
        Return gateways that support a given capability.
        Example:
            gateways_supporting("supports_cards")
            gateways_supporting("supports_refunds")
        """
        supported = []

        for name in self.registry.list():
            gateway = self.registry.get(name)

            caps = getattr(gateway, "capabilities", None)
            if caps is None:
                continue

            if getattr(caps, capability, False):
                supported.append(name)

        return supported
