from trading.orchestrator import TradingOrchestrator
from trading.risk.engine import RiskEngine
from trading.risk.policy import RiskPolicy
from trading.risk.state import RiskState

orchestrator = TradingOrchestrator(RiskEngine(RiskPolicy()))
state = RiskState(10000, 10000, 10000, recent_trade_times=[100, 150, 199])
risk_input = orchestrator.build_risk_input(state, 0.005, 500, now=200)
assert risk_input.trades_last_minute == 2
print("ORCHESTRATOR_TRADE_RATE_MAPPING: PASS")
