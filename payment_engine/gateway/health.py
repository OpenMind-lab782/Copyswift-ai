class GatewayHealthMonitor:
    """
    Tracks the health status of registered payment gateways.
    """

    def __init__(self):
        self._statuses = {}

    def set_status(self, gateway, status):
        self._statuses[gateway] = status

    def get_status(self, gateway):
        return self._statuses.get(gateway, "unknown")

    def list(self):
        return dict(self._statuses)

    def clear(self):
        self._statuses.clear()
