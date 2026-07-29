from collections import defaultdict


class GatewayHealthMonitor:
    def __init__(self):
        self._stats = defaultdict(lambda: {
            "success": 0,
            "failure": 0,
        })

    def record_success(self, gateway):
        self._stats[gateway]["success"] += 1

    def record_failure(self, gateway):
        self._stats[gateway]["failure"] += 1

    def snapshot(self):
        result = {}

        for gateway, stats in self._stats.items():
            total = stats["success"] + stats["failure"]

            result[gateway] = {
                **stats,
                "total": total,
                "success_rate": (
                    stats["success"] / total
                    if total else 0.0
                ),
            }

        return result
