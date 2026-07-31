import time


class RateLimiter:
    """
    Simple in-memory rate limiter.

    Development version.
    Future versions can use Redis.
    """

    def __init__(self, limit=60, window=60):
        self.limit = limit
        self.window = window
        self.requests = {}

    def allow(self, client_id):
        now = time.time()

        history = self.requests.get(client_id, [])

        history = [
            timestamp
            for timestamp in history
            if now - timestamp < self.window
        ]

        if len(history) >= self.limit:
            self.requests[client_id] = history
            return False

        history.append(now)

        self.requests[client_id] = history

        return True

    def remaining(self, client_id):
        history = self.requests.get(client_id, [])

        return max(
            0,
            self.limit - len(history)
        )
