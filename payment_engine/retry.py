import time


class RetryPolicy:
    """Simple retry policy."""

    def __init__(self, retries=3, delay=0.0):
        self.retries = retries
        self.delay = delay

    def execute(self, func, *args, **kwargs):
        last_error = None

        for attempt in range(self.retries):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                last_error = exc

                if attempt < self.retries - 1 and self.delay > 0:
                    time.sleep(self.delay)

        raise last_error
