from decimal import Decimal, ROUND_DOWN

RISK_QUANTUM = Decimal("0.00000001")

def risk_decimal(value) -> Decimal:
    return Decimal(str(value))

def normalize_risk(value) -> Decimal:
    return risk_decimal(value).quantize(RISK_QUANTUM, rounding=ROUND_DOWN)
