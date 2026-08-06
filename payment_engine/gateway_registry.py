class GatewayRegistry:
    """
    Central registry for all payment gateways.
    """

    def __init__(self):
        self._gateways = {}

    def register(self, gateway):
        self._gateways[gateway.name] = gateway

    def get(self, name):
        return self._gateways.get(name)

    def exists(self, name):
        return name in self._gateways

    def names(self):
        return sorted(self._gateways.keys())

    def all(self):
        return dict(self._gateways)
