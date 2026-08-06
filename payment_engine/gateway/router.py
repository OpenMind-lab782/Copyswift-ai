class GatewayRouter:
    """
    Gateway Router.

    Responsible for selecting the appropriate
    payment gateway from the GatewayRegistry.
    """

    def __init__(self, registry):
        self.registry = registry

    def route(self, gateway_name):
        return self.registry.get(gateway_name)
