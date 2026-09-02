from trading.orchestrator import TradingOrchestrator
from trading.risk.engine import RiskEngine
from trading.risk.policy import RiskPolicy
from trading.strategies.signal import TradingSignal

orchestrator = TradingOrchestrator(RiskEngine(RiskPolicy()))
signal = TradingSignal("TEST", "HOLD", 0.0, 100.0, "flat")
result = orchestrator.evaluate_signal(signal)
assert result is None
print("ORCHESTRATOR_HOLD_DECISION: PASS")
