from trading.risk.engine import RiskEngine
from trading.risk.input import RiskInput
from trading.risk.policy import RiskPolicy
from trading.risk.position_sizer import PositionSizer
from trading.risk.sizing import PositionSizingInput

sized = PositionSizer().calculate(PositionSizingInput(10000, 0.01, 100, 98, 1, 1, 1, 4000))
decision = RiskEngine(RiskPolicy()).evaluate(RiskInput(10000, 10000, 10000, sized["risk_fraction"], sized["notional"], 0, 0, 0))

assert sized["quantity"] == 40.0
assert sized["notional"] == 4000.0
assert sized["risk_fraction"] == 0.008
assert decision.allowed is True
assert decision.action == "ALLOW"
assert decision.reason_code == "RISK_CHECK_PASSED"
assert decision.risk_fraction == sized["risk_fraction"]
assert decision.approved_notional == sized["notional"]
assert decision.validate() is True
print("POSITION_SIZER_RISK_ENGINE_INTEGRATION: PASS")
