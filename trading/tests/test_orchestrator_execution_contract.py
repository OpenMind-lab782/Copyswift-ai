from trading.orchestrator import TradingOrchestrator
from trading.execution.broker import BrokerAdapter, OrderRequest, OrderResult
from trading.risk.decision import RiskDecision
from trading.risk.engine import RiskEngine
from trading.risk.policy import RiskPolicy

class FakeBroker(BrokerAdapter):
    def __init__(self):
        self.orders = []
    def place_order(self, order):
        self.orders.append(order)
        return OrderResult("UNEXPECTED", "FILLED", {})

orchestrator = TradingOrchestrator(RiskEngine(RiskPolicy()))
broker = FakeBroker()
order = OrderRequest("TEST", "BUY", 1)
malformed = RiskDecision(False, "ALLOW", "RISK_CHECK_PASSED", "invalid")
try:
    orchestrator.execute_order(broker, order, malformed)
except ValueError:
    pass
else:
    raise AssertionError("malformed ALLOW decision must be rejected")
assert len(broker.orders) == 0
print("EXECUTION_GATE_CONTRACT: PASS")