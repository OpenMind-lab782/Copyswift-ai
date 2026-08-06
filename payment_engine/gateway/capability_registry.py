class GatewayCapabilityRegistry:
    """
    Stores the capabilities supported by each payment gateway.
    """

    def __init__(self):
        self._capabilities = {}

    def register(self, gateway, **capabilities):
        self._capabilities[gateway] = dict(capabilities)

    def get(self, gateway):
        return self._capabilities.get(gateway)

    def list(self):
        return sorted(self._capabilities.keys())

    def clear(self):
        self._capabilities.clear()
