from trading.risk.state import RiskState

def expect_rejection(**overrides):
    values = {"equity": 10000, "starting_daily_equity": 10000, "peak_equity": 10000}
    values.update(overrides)
    try:
        RiskState(**values).validate()
    except ValueError:
        return True
    return False

assert RiskState(equity=10000, starting_daily_equity=10000, peak_equity=10000).validate() is True
assert expect_rejection(equity=0)
assert expect_rejection(starting_daily_equity=0)
assert expect_rejection(peak_equity=0)
assert expect_rejection(open_risk=-1)
assert expect_rejection(open_notional=-1)
print("RISK_STATE_TESTS: PASS")
