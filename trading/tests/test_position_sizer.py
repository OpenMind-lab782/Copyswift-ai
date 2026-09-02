from trading.risk.position_sizer import PositionSizer
from trading.risk.sizing import PositionSizingInput

sizer = PositionSizer()

r = sizer.calculate(PositionSizingInput(10000, 0.01, 100, 98, 1, 1, 1, 4000))
assert r == {"quantity": 40.0, "notional": 4000.0, "risk_amount": 80.0, "risk_fraction": 0.008}

r = sizer.calculate(PositionSizingInput(10000, 0.02, 100, 90, 1, 0, 1, 1500))
assert r == {"quantity": 15.0, "notional": 1500.0, "risk_amount": 150.0, "risk_fraction": 0.015}

r = sizer.calculate(PositionSizingInput(10000, 0.01, 100, 98, 1, 0, 3, 0))
assert r == {"quantity": 48.0, "notional": 4800.0, "risk_amount": 96.0, "risk_fraction": 0.0096}

r = sizer.calculate(PositionSizingInput(10000, 0.001, 100, 98, 1, 50, 1, 0))
assert r == {"quantity": 0.0, "notional": 0.0, "risk_amount": 0.0, "risk_fraction": 0.0}

print("POSITION_SIZER_TESTS: PASS")
