from trading.orchestrator import TradingOrchestrator
from trading.execution.broker import BrokerAdapter, OrderRequest, OrderResult
from trading.risk.decision import RiskDecision
from trading.risk.engine import RiskEngine
from trading.risk.policy import RiskPolicy
from trading.portfolio.accounting import PortfolioAccounting
from trading.portfolio.intent import PositionIntent

class GateBroker(BrokerAdapter):
    def __init__(self):
        self.orders = []
    def place_order(self, order):
        order.validate()
        self.orders.append(order)
        return OrderResult("GATE-" + str(len(self.orders)), "FILLED", {"symbol": order.symbol, "side": order.side, "quantity": order.quantity, "filled_quantity": order.quantity, "fill_price": 100.0})

orchestrator = TradingOrchestrator(RiskEngine(RiskPolicy()))
decision = RiskDecision(True, "ALLOW", "OK", "allowed")

# CLOSE_LONG with zero LONG inventory must never reach broker.
broker = GateBroker()
accounting = PortfolioAccounting()
close_long = OrderRequest("GATE-LONG", "SELL", 2.0, intent=PositionIntent.CLOSE_LONG)
try:
    orchestrator.execute_order(broker, close_long, decision, accounting)
except ValueError:
    pass
else:
    raise AssertionError("insufficient LONG inventory must be rejected")
assert len(broker.orders) == 0
assert accounting.ledger.get_inventory("GATE-LONG", "LONG") == 0.0

# CLOSE_SHORT with zero SHORT inventory must never reach broker.
close_short = OrderRequest("GATE-SHORT", "BUY", 2.0, intent=PositionIntent.CLOSE_SHORT)
try:
    orchestrator.execute_order(broker, close_short, decision, accounting)
except ValueError:
    pass
else:
    raise AssertionError("insufficient SHORT inventory must be rejected")
assert len(broker.orders) == 0
assert accounting.ledger.get_inventory("GATE-SHORT", "SHORT") == 0.0

# Any close order without accounting must be rejected before broker execution.
no_accounting = OrderRequest("GATE-NO-ACCOUNT", "SELL", 1.0, intent=PositionIntent.CLOSE_LONG)
try:
    orchestrator.execute_order(broker, no_accounting, decision)
except ValueError:
    pass
else:
    raise AssertionError("close order without accounting must be rejected")
assert len(broker.orders) == 0

# Valid close must pass the pre-execution gate and reach broker.
open_order = OrderRequest("GATE-VALID", "BUY", 3.0, intent=PositionIntent.OPEN_LONG)
open_result = orchestrator.execute_order(broker, open_order, decision, accounting)
assert open_result.status == "FILLED"
assert accounting.ledger.get_inventory("GATE-VALID", "LONG") == 3.0
valid_close = OrderRequest("GATE-VALID", "SELL", 2.0, intent=PositionIntent.CLOSE_LONG)
close_result = orchestrator.execute_order(broker, valid_close, decision, accounting)
assert close_result.status == "FILLED"
assert len(broker.orders) == 2
assert accounting.ledger.get_inventory("GATE-VALID", "LONG") == 1.0

print("PRE_EXECUTION_LONG_REJECTION: PASS")
print("PRE_EXECUTION_SHORT_REJECTION: PASS")
print("PRE_EXECUTION_NO_ACCOUNTING: PASS")
print("PRE_EXECUTION_VALID_CLOSE: PASS")
print("PRE_EXECUTION_INVENTORY_GATE: PASS")
