from trading.risk.engine import RiskEngine
from trading.risk.input import RiskInput
from trading.risk.policy import RiskPolicy

base = dict(equity=10000, starting_daily_equity=10000, peak_equity=10000, proposed_risk_fraction=0.005, proposed_notional=1000, open_risk_fraction=0.0, open_notional_fraction=0.0, trades_last_minute=0)
decision = RiskEngine(RiskPolicy()).evaluate(RiskInput(**base))
assert decision.allowed is True
assert decision.action == "ALLOW"
assert decision.reason_code == "RISK_CHECK_PASSED"
assert decision.risk_fraction == 0.005
assert decision.approved_notional == 1000
assert decision.validate() is True
print("RISK_ENGINE_ALLOW_TEST: PASS")
