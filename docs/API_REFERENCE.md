# Swift Payment Engine v2.0.0

# API Reference

## PaymentEngine

The main entry point into the payment engine.

```python
from payment_engine.engine import PaymentEngine

engine = PaymentEngine()
```

---

## verify_payment()

Verify a payment using a registered gateway.

### Syntax

```python
engine.verify_payment(
    gateway,
    reference
)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| gateway | str | Registered gateway name |
| reference | str | Payment reference |

### Example

```python
result = engine.verify_payment(
    "paystack",
    "PAYMENT-001"
)
```

### Success Response

```python
{
    "success": True,
    "gateway": "paystack",
    "status": "verified",
    "reference": "PAYMENT-001",
    "correlation_id": "..."
}
```

---

## refund_payment()

Refund a verified payment.

```python
engine.refund_payment(
    "paystack",
    "PAYMENT-001"
)
```

---

## handle_webhook()

Process incoming webhook events.

```python
engine.handle_webhook(
    "paystack",
    payload
)
```

---

## Supported Gateways

- Paystack
- Flutterwave
- DPO
- Crypto

---

## Exceptions

The engine may raise:

- CircuitOpenError
- PaymentGatewayError
- DuplicatePaymentError
- GatewayNotFoundError

---

## Version

Swift Payment Engine v2.0.0
