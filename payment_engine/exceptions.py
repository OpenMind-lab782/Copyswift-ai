class PaymentEngineError(Exception):
    """Base exception for all payment engine errors."""


class GatewayError(PaymentEngineError):
    """Raised for gateway-related failures."""


class GatewayNotFoundError(GatewayError):
    """Raised when a requested gateway is not registered."""


class DuplicateReferenceError(PaymentEngineError):
    """Raised when a payment reference has already been processed."""


class PaymentTimeoutError(PaymentEngineError):
    """Raised when a payment operation exceeds the configured timeout."""


class CircuitBreakerOpenError(PaymentEngineError):
    """Raised when the circuit breaker is open."""
