class GatewayRegistry:

    def __init__(self):
        self._gateways = {}

    def register(self, name, gateway):
        self._gateways[name] = gateway
        return gateway

    def get(self, name):
        return self._gateways.get(name)

    def list(self):
        return sorted(self._gateways.keys())

    def clear(self):
        self._gateways.clear()
