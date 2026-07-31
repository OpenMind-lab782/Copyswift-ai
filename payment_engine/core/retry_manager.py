import time


class RetryManager:
    """
    Simple retry manager for transient failures.
    """

    def __init__(self, retries=3, delay=1):
        self.retries = retries
        self.delay = delay

    def execute(self, func, *args, **kwargs):
        last_exception = None

        for attempt in range(1, self.retries + 1):
            try:
                return func(*args, **kwargs)

            except Exception as exc:
                last_exception = exc

                if attempt < self.retries:
                    time.sleep(self.delay)

        raise last_exception
