class GatewayRegistry:

    def __init__(self):
        self._gateways = {}

    def register(self, gateway):
        self._gateways[gateway.name] = gateway

    def get(self, name):
        return self._gateways.get(name)

    def list(self):
        return sorted(self._gateways.keys())
