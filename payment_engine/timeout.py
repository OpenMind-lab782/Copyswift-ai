import time


class TimeoutError(Exception):
    """Raised when an operation exceeds the configured timeout."""


class TimeoutPolicy:
    def __init__(self, timeout=5.0):
        self.timeout = timeout

    def execute(self, func, *args, **kwargs):
        start = time.monotonic()

        result = func(*args, **kwargs)

        elapsed = time.monotonic() - start

        if elapsed > self.timeout:
            raise TimeoutError(
                f"Operation exceeded timeout ({elapsed:.3f}s > {self.timeout:.3f}s)"
            )

        return result
