import unittest

from payment_engine.exceptions import (
    PaymentEngineError,
    GatewayError,
    GatewayNotFoundError,
    DuplicateReferenceError,
    PaymentTimeoutError,
    CircuitBreakerOpenError,
)


class TestExceptions(unittest.TestCase):

    def test_gateway_error(self):
        self.assertTrue(issubclass(GatewayError, PaymentEngineError))

    def test_gateway_not_found(self):
        self.assertTrue(issubclass(GatewayNotFoundError, GatewayError))

    def test_duplicate_reference(self):
        self.assertTrue(issubclass(DuplicateReferenceError, PaymentEngineError))

    def test_timeout(self):
        self.assertTrue(issubclass(PaymentTimeoutError, PaymentEngineError))

    def test_circuit_breaker(self):
        self.assertTrue(issubclass(CircuitBreakerOpenError, PaymentEngineError))


if __name__ == "__main__":
    unittest.main()
