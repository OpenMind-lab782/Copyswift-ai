from trading.risk.engine import RiskEngine
from trading.risk.input import RiskInput
from trading.risk.policy import RiskPolicy

BASE = dict(equity=10000, starting_daily_equity=10000, peak_equity=10000, proposed_risk_fraction=0.005, proposed_notional=1000, open_risk_fraction=0.0, open_notional_fraction=0.0, trades_last_minute=0)
engine = RiskEngine(RiskPolicy())

def check(overrides, action, code):
    values = BASE.copy(); values.update(overrides)
    decision = engine.evaluate(RiskInput(**values))
    assert decision.action == action, (decision, action)
    assert decision.allowed is (action == "ALLOW"), (decision, action)
    assert decision.reason_code == code, (decision, code)
    assert decision.validate() is True

check({"equity": 0}, "REJECT", "INVALID_RISK_INPUT")
check({"kill_switch": True}, "REJECT", "KILL_SWITCH_ACTIVE")
check({"broker_state_known": False}, "REJECT", "BROKER_STATE_UNKNOWN")
check({"stale_market_data": True}, "REJECT", "STALE_MARKET_DATA")
check({"price_valid": False}, "REJECT", "INVALID_PRICE")
check({"equity": 9700}, "REJECT", "DAILY_LOSS_LIMIT")
check({"equity": 10800, "peak_equity": 12000}, "REJECT", "MAX_DRAWDOWN")
check({"proposed_risk_fraction": 0.02}, "REDUCE", "TRADE_RISK_LIMIT")
check({"open_risk_fraction": 0.028, "proposed_risk_fraction": 0.005}, "REDUCE", "OPEN_RISK_LIMIT")
check({"open_notional_fraction": 0.95, "proposed_notional": 1000}, "REDUCE", "OPEN_NOTIONAL_LIMIT")
check({"trades_last_minute": 5}, "REJECT", "TRADE_RATE_LIMIT")
check({"duplicate": True}, "REJECT", "DUPLICATE_ORDER")
print("RISK_ENGINE_REJECTION_MATRIX: PASS")
