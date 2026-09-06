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
        return OrderResult("TEST-ALLOW-1", "FILLED", {"symbol": order.symbol, "side": order.side, "quantity": order.quantity, "filled_quantity": order.quantity, "fill_price": 100.0})

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
from trading.portfolio.accounting import PortfolioAccounting
from trading.portfolio.intent import PositionIntent
accounting = PortfolioAccounting()
accounting_order = OrderRequest("ACCOUNTING", "BUY", 3.0, intent=PositionIntent.OPEN_LONG)
accounting_result = orchestrator.execute_order(broker, accounting_order, decision, accounting)
assert accounting_result.status == "FILLED"
assert accounting.ledger.get_inventory("ACCOUNTING", "LONG") == 3.0
print("ORCHESTRATOR_ACCOUNTING_INTEGRATION: PASS")

from trading.portfolio.accounting import account_submitted_order
partial_accounting = PortfolioAccounting()
partial_order = OrderRequest("PARTIAL", "BUY", 5.0, intent=PositionIntent.OPEN_LONG)
fill1 = OrderResult("PART-001", "FILLED", {"symbol": "PARTIAL", "side": "BUY", "quantity": 5.0, "filled_quantity": 2.0, "fill_price": 100.0})
fill2 = OrderResult("PART-002", "FILLED", {"symbol": "PARTIAL", "side": "BUY", "quantity": 5.0, "filled_quantity": 3.0, "fill_price": 101.0})
fill2_timestamp = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
account_submitted_order(partial_order, fill1, fill2_timestamp, partial_accounting)
assert partial_accounting.ledger.get_inventory("PARTIAL", "LONG") == 2.0
account_submitted_order(partial_order, fill2, fill2_timestamp, partial_accounting)
assert partial_accounting.ledger.get_inventory("PARTIAL", "LONG") == 5.0
try:
    account_submitted_order(partial_order, fill2, fill2_timestamp, partial_accounting)
except ValueError:
    pass
else:
    raise AssertionError("duplicate fill must be rejected")
assert partial_accounting.ledger.get_inventory("PARTIAL", "LONG") == 5.0
print("PARTIAL_FILL_DUPLICATE_SAFETY: PASS")

class CloseBroker(BrokerAdapter):
    def place_order(self, order):
        order.validate()
        self.orders.append(order)
        return OrderResult("ROUND-"+str(len(self.orders)), "FILLED", {"symbol": order.symbol, "side": order.side, "quantity": order.quantity, "filled_quantity": order.quantity, "fill_price": next(self.prices)})

close_broker=CloseBroker()
close_broker.orders=[]
close_broker.prices=iter([100.0,105.0,110.0,120.0])
round_accounting=PortfolioAccounting()
round_orch=TradingOrchestrator(RiskEngine(RiskPolicy()))
open_round=OrderRequest("ROUND", "BUY", 5.0, intent=PositionIntent.OPEN_LONG)
round_orch.execute_order(close_broker, open_round, decision, round_accounting)
assert round_accounting.ledger.get_inventory("ROUND", "LONG") == 5.0
close_one=OrderRequest("ROUND", "SELL", 2.0, intent=PositionIntent.CLOSE_LONG)
r1=round_orch.execute_order(close_broker, close_one, decision, round_accounting)
assert r1.status == "FILLED"
assert round_accounting.ledger.get_inventory("ROUND", "LONG") == 3.0
close_two=OrderRequest("ROUND", "SELL", 3.0, intent=PositionIntent.CLOSE_LONG)
r2=round_orch.execute_order(close_broker, close_two, decision, round_accounting)
assert r2.status == "FILLED"
assert round_accounting.ledger.get_inventory("ROUND", "LONG") == 0.0
assert round_accounting.ledger.get_positions("ROUND") == []
try:
    over_close=OrderRequest("ROUND", "SELL", 1.0, intent=PositionIntent.CLOSE_LONG)
    round_orch.execute_order(close_broker, over_close, decision, round_accounting)
except ValueError:
    pass
else:
    raise AssertionError("over-close must be rejected")
assert round_accounting.ledger.get_inventory("ROUND", "LONG") == 0.0
print("ROUND_TRIP_CLOSE_LIFECYCLE: PASS")
