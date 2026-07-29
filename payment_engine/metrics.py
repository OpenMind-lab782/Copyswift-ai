from collections import Counter


class MetricsCollector:
    def __init__(self):
        self._metrics = Counter()

    def increment(self, name, amount=1):
        self._metrics[name] += amount

    def get(self, name):
        return self._metrics.get(name, 0)

    def snapshot(self):
        return dict(self._metrics)

    def reset(self):
        self._metrics.clear()
