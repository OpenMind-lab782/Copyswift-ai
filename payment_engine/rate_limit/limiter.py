import time

from payment_engine.exceptions import ValidationError


class RateLimiter:
    def __init__(self, limit=60, window=60):
        self.limit = limit
        self.window = window
        self.requests = {}

    def check(self, key):
        now = time.time()

        timestamps = self.requests.get(key, [])

        timestamps = [
            ts for ts in timestamps
            if now - ts < self.window
        ]

        if len(timestamps) >= self.limit:
            raise ValidationError(
                "Rate limit exceeded."
            )

        timestamps.append(now)
        self.requests[key] = timestamps

        return True
