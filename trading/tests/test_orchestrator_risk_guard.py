from trading.execution.broker import BrokerAdapter, OrderRequest, OrderResult
from trading.orchestrator import TradingOrchestrator
from trading.risk.engine import RiskEngine
from trading.risk.policy import RiskPolicy
from trading.risk.state import RiskState

class FakeBroker(BrokerAdapter):
    def __init__(self):
        self.orders = []
    def place_order(self, order):
        self.orders.append(order)
        return OrderResult("TEST-1", "FILLED", {})

broker = FakeBroker()
orchestrator = TradingOrchestrator(RiskEngine(RiskPolicy()))
state = RiskState(10000, 10000, 10000, kill_switch=True)
risk_input = orchestrator.build_risk_input(state, 0.005, 500, now=200, order_key="TEST|BUY|5.0|100.0")
decision = orchestrator.risk_engine.evaluate(risk_input)
assert decision.allowed is False
assert decision.reason_code == "KILL_SWITCH_ACTIVE"
assert len(broker.orders) == 0
print("ORCHESTRATOR_RISK_REJECTION_GUARD: PASS")
