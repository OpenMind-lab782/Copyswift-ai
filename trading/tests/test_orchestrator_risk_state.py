from trading.orchestrator import TradingOrchestrator
from trading.risk.engine import RiskEngine
from trading.risk.policy import RiskPolicy
from trading.risk.state import RiskState

orchestrator = TradingOrchestrator(RiskEngine(RiskPolicy()))
state = RiskState(10000, 10000, 10000, open_risk=100, open_notional=2000)
state.validate()
risk_input = orchestrator.build_risk_input(state, 0.005, 500)
assert risk_input.equity == 10000
assert risk_input.starting_daily_equity == 10000
assert risk_input.peak_equity == 10000
assert risk_input.open_risk_fraction == 0.01
assert risk_input.open_notional_fraction == 0.2
assert risk_input.proposed_risk_fraction == 0.005
assert risk_input.proposed_notional == 500
print("ORCHESTRATOR_RISK_STATE_MAPPING: PASS")
