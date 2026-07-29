import unittest

from payment_engine.circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
)


class TestCircuitBreaker(unittest.TestCase):

    def test_success(self):
        breaker = CircuitBreaker()

        result = breaker.execute(lambda: "OK")

        self.assertEqual(result, "OK")

    def test_opens_after_failures(self):
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=60,
        )

        def fail():
            raise RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            breaker.execute(fail)

        with self.assertRaises(RuntimeError):
            breaker.execute(fail)

        with self.assertRaises(CircuitOpenError):
            breaker.execute(lambda: "never")


if __name__ == "__main__":
    unittest.main()
