from trading.orchestrator import TradingOrchestrator
from trading.risk.engine import RiskEngine
from trading.risk.policy import RiskPolicy
from trading.risk.state import RiskState

orchestrator = TradingOrchestrator(RiskEngine(RiskPolicy()))
state = RiskState(10000, 10000, 10000, recent_order_keys={"TEST|BUY|10.0|100.0": 100})
risk_input = orchestrator.build_risk_input(state, 0.005, 500, now=200, order_key="TEST|BUY|10.0|100.0")
assert risk_input.duplicate is False
print("ORCHESTRATOR_DUPLICATE_WINDOW: PASS")
