import time


class LatencyRecorder:
    def __init__(self):
        self._samples = {}

    def record(self, name, duration):
        self._samples.setdefault(name, []).append(duration)

    def average(self, name):
        values = self._samples.get(name, [])
        if not values:
            return 0.0
        return sum(values) / len(values)

    def count(self, name):
        return len(self._samples.get(name, []))

    def snapshot(self):
        return {
            name: {
                "count": len(values),
                "average": sum(values) / len(values) if values else 0.0,
            }
            for name, values in self._samples.items()
        }


class Timer:
    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self._start
