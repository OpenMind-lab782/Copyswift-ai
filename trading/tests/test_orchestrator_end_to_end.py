from trading.orchestrator import TradingOrchestrator
from trading.execution.broker import BrokerAdapter, OrderResult
from trading.risk.decision import RiskDecision
from trading.risk.engine import RiskEngine
from trading.risk.policy import RiskPolicy
from trading.strategies.signal import TradingSignal

class FakeBroker(BrokerAdapter):
    def __init__(self):
        self.orders = []
    def place_order(self, order):
        order.validate()
        self.orders.append(order)
        return OrderResult("E2E-1", "FILLED", {})

orchestrator = TradingOrchestrator(RiskEngine(RiskPolicy()))
broker = FakeBroker()
signal = TradingSignal("TEST", "BUY", 0.9, 100.0, "momentum")
sizing = {"quantity": 5.0, "notional": 500.0, "risk_amount": 5.0, "risk_fraction": 0.0005}
decision = RiskDecision(True, "ALLOW", "RISK_CHECK_PASSED", "approved", 0.0005, 500.0)
order = orchestrator.build_order(signal, sizing, stop_loss=99.0)
result = orchestrator.execute_order(broker, order, decision)
assert result.status == "FILLED"
assert len(broker.orders) == 1
assert broker.orders[0].symbol == "TEST"
assert broker.orders[0].side == "BUY"
assert broker.orders[0].quantity == 5.0
assert broker.orders[0].stop_loss == 99.0
print("ORCHESTRATOR_END_TO_END: PASS")