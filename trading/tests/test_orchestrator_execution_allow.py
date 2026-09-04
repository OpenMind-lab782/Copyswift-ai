from trading.orchestrator import TradingOrchestrator
from trading.execution.broker import BrokerAdapter, OrderRequest, OrderResult
from trading.risk.decision import RiskDecision
from trading.risk.engine import RiskEngine
from trading.risk.policy import RiskPolicy

class FakeBroker(BrokerAdapter):
    def __init__(self):
        self.orders = []
    def place_order(self, order):
        order.validate()
        self.orders.append(order)
        return OrderResult("TEST-ALLOW-1", "FILLED", {})

orchestrator = TradingOrchestrator(RiskEngine(RiskPolicy()))
broker = FakeBroker()
order = OrderRequest("TEST", "BUY", 1)
decision = RiskDecision(True, "ALLOW", "RISK_CHECK_PASSED", "approved", 0.005, 100)
result = orchestrator.execute_order(broker, order, decision)
assert result.status == "FILLED"
assert result.broker_order_id == "TEST-ALLOW-1"
assert len(broker.orders) == 1
assert broker.orders[0] == order
print("EXECUTION_GATE_ALLOW: PASS")