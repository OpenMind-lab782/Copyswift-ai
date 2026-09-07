from decimal import Decimal, ROUND_DOWN
RISK_QUANTUM = Decimal("0.00000001")

def validate_risk_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal, str)):
        raise ValueError("risk value must be numeric")
    try:
        number = Decimal(str(value))
    except Exception as exc:
        raise ValueError("risk value must be numeric") from exc
    if not number.is_finite():
        raise ValueError("risk value must be finite")
    return number

def risk_decimal(value) -> Decimal:
    return validate_risk_number(value)

def normalize_risk(value) -> Decimal:
    return risk_decimal(value).quantize(RISK_QUANTUM, rounding=ROUND_DOWN)
