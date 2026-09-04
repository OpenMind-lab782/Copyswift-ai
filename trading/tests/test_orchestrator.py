from trading.orchestrator import TradingOrchestrator
from trading.risk.engine import RiskEngine
from trading.risk.policy import RiskPolicy

engine = RiskEngine(RiskPolicy())
orchestrator = TradingOrchestrator(engine)
assert orchestrator.risk_engine is engine
print("ORCHESTRATOR_CONSTRUCTOR_CONTRACT: PASS")
