from datetime import UTC, datetime
from trading.market.provider import MarketTick
from trading.strategies.momentum import MomentumStrategy

ticks = [MarketTick("TEST", 100, 100, datetime.now(UTC)) for _ in range(20)]
signal = MomentumStrategy(lookback=20).evaluate(ticks)
assert signal.action == "HOLD"
print("ORCHESTRATION_HOLD_BASELINE: PASS")
from trading.risk.engine import RiskEngine
from trading.risk.input import RiskInput
from trading.risk.policy import RiskPolicy
from trading.risk.position_sizer import PositionSizer
from trading.risk.sizing import PositionSizingInput

sized = PositionSizer().calculate(PositionSizingInput(10000, 0.01, 102, 100, 1, 1, 1, 4000))
decision = RiskEngine(RiskPolicy()).evaluate(RiskInput(10000, 10000, 10000, sized["risk_fraction"], sized["notional"], 0, 0, 0))
assert decision.allowed is True
assert decision.action == "ALLOW"
assert decision.reason_code == "RISK_CHECK_PASSED"
print("ORCHESTRATION_BUY_RISK_BASELINE: PASS")
