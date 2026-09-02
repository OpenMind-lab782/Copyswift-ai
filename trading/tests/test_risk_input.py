from trading.risk.input import RiskInput

BASE = dict(equity=10000, starting_daily_equity=10000, peak_equity=10000, proposed_risk_fraction=0.005, proposed_notional=1000, open_risk_fraction=0, open_notional_fraction=0, trades_last_minute=0)

def expect_rejection(overrides):
    values = BASE.copy(); values.update(overrides)
    try:
        RiskInput(**values).validate()
    except ValueError:
        return True
    return False

assert expect_rejection({"proposed_risk_fraction": -0.001})
assert expect_rejection({"proposed_notional": -1})
assert expect_rejection({"open_risk_fraction": -0.001})
assert expect_rejection({"open_notional_fraction": -0.001})
assert expect_rejection({"trades_last_minute": -1})
assert RiskInput(**BASE).validate() is True
print("RISK_INPUT_BOUNDARY_TESTS: PASS")
