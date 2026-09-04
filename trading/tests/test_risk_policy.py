from trading.risk.policy import RiskPolicy

def expect_rejection(**kwargs):
    try:
        RiskPolicy(**kwargs).validate()
    except ValueError:
        return True
    return False

assert RiskPolicy().validate() is True
assert expect_rejection(max_risk_per_trade=0)
assert expect_rejection(max_daily_loss=0)
assert expect_rejection(max_drawdown=0)
assert expect_rejection(duplicate_window_seconds=0)
print("RISK_POLICY_TESTS: PASS")
