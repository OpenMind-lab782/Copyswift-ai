from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class GatewayHealth:
    name: str
    status: str = "ONLINE"
    success_count: int = 0
    failure_count: int = 0
    last_success: str = ""
    last_error: str = ""

    def record_success(self):
        self.success_count += 1
        self.last_success = datetime.now(timezone.utc).isoformat()
        self.status = "ONLINE"

    def record_failure(self, error):
        self.failure_count += 1
        self.last_error = str(error)
        self.status = "DEGRADED"

    def as_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "last_success": self.last_success,
            "last_error": self.last_error,
        }


class HealthRegistry:

    def __init__(self):
        self._gateways = {}

    def get(self, gateway_name):
        if gateway_name not in self._gateways:
            self._gateways[gateway_name] = GatewayHealth(gateway_name)
        return self._gateways[gateway_name]

    def all(self):
        return {
            name: health.as_dict()
            for name, health in self._gateways.items()
        }
