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
        return OrderResult("TEST-1", "FILLED", {})

orchestrator = TradingOrchestrator(RiskEngine(RiskPolicy()))
broker = FakeBroker()
order = OrderRequest("TEST", "BUY", 1)
reject = RiskDecision(False, "REJECT", "DAILY_LOSS_LIMIT", "blocked")
reduce = RiskDecision(False, "REDUCE", "TRADE_RISK_LIMIT", "reduce")

for decision in (reject, reduce):
    try:
        orchestrator.execute_order(broker, order, decision)
    except ValueError:
        pass
    else:
        raise AssertionError("non-ALLOW decision must block execution")

assert len(broker.orders) == 0
print("EXECUTION_GATE_REJECTION: PASS")