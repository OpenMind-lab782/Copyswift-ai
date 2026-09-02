from trading.orchestrator import TradingOrchestrator
from trading.risk.engine import RiskEngine
from trading.risk.policy import RiskPolicy
from trading.risk.state import RiskState

orchestrator = TradingOrchestrator(RiskEngine(RiskPolicy()))
state = RiskState(10000, 10000, 10000, kill_switch=True)
decision = orchestrator.evaluate_risk(state, 0.005, 500, now=200, order_key="TEST|BUY|5.0|100.0")
assert decision.allowed is False
assert decision.action == "REJECT"
assert decision.reason_code == "KILL_SWITCH_ACTIVE"
print("ORCHESTRATOR_RISK_GATE: PASS")
