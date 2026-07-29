import time


class CircuitOpenError(Exception):
    """Raised when the circuit breaker is open."""


class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.last_failure = None

    def execute(self, func, *args, **kwargs):
        if self.is_open():
            raise CircuitOpenError("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self.reset()
            return result
        except Exception:
            self.failure_count += 1
            self.last_failure = time.monotonic()
            raise

    def is_open(self):
        if self.failure_count < self.failure_threshold:
            return False

        if self.last_failure is None:
            return False

        if (time.monotonic() - self.last_failure) >= self.recovery_timeout:
            self.reset()
            return False

        return True

    def reset(self):
        self.failure_count = 0
        self.last_failure = None
