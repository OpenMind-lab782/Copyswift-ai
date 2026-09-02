from decimal import Decimal
from trading.risk.numeric import RISK_QUANTUM, normalize_risk, risk_decimal

assert RISK_QUANTUM == Decimal("0.00000001")
assert risk_decimal(0.12345678) == Decimal("0.12345678")
assert risk_decimal("0.123456789") == Decimal("0.123456789")
assert normalize_risk("0.123456789") == Decimal("0.12345678")
assert normalize_risk("0.1234567899") == Decimal("0.12345678")
assert normalize_risk("1.999999999") == Decimal("1.99999999")
assert normalize_risk("-0.123456789") == Decimal("-0.12345678")
print("RISK_NUMERIC_TESTS: PASS")
