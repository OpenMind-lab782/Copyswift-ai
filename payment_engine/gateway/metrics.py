class GatewayMetrics:
    """
    Tracks basic gateway performance metrics.
    """

    def __init__(self):
        self._metrics = {}

    def _entry(self, gateway):
        return self._metrics.setdefault(
            gateway,
            {
                "success": 0,
                "failure": 0,
            },
        )

    def record_success(self, gateway):
        self._entry(gateway)["success"] += 1

    def record_failure(self, gateway):
        self._entry(gateway)["failure"] += 1

    def get(self, gateway):
        return dict(
            self._metrics.get(
                gateway,
                {
                    "success": 0,
                    "failure": 0,
                },
            )
        )

    def list(self):
        return {
            gateway: dict(values)
            for gateway, values in self._metrics.items()
        }

    def clear(self):
        self._metrics.clear()
