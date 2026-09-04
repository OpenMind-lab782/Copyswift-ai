from trading.orchestrator import TradingOrchestrator
from trading.risk.engine import RiskEngine
from trading.risk.policy import RiskPolicy

orchestrator = TradingOrchestrator(RiskEngine(RiskPolicy()))
key = orchestrator.build_order_key("TEST", "BUY", 10.0, 100.0)
assert key == "TEST|BUY|10.0|100.0"
assert orchestrator.build_order_key("TEST", "BUY", 10.0, 100.0) == key
print("ORCHESTRATOR_ORDER_KEY_CONTRACT: PASS")
