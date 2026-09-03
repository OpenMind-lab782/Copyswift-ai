from trading.orchestrator import TradingOrchestrator
from trading.execution.broker import OrderRequest
from trading.risk.engine import RiskEngine
from trading.risk.policy import RiskPolicy
from trading.strategies.signal import TradingSignal

orchestrator = TradingOrchestrator(RiskEngine(RiskPolicy()))
sizing = {"quantity": 5.0, "notional": 500.0, "risk_amount": 5.0, "risk_fraction": 0.0005}
buy = TradingSignal("TEST", "BUY", 0.9, 100.0, "momentum")
sell = TradingSignal("TEST", "SELL", 0.9, 100.0, "momentum")
hold = TradingSignal("TEST", "HOLD", 0.5, 100.0, "no momentum")

buy_order = orchestrator.build_order(buy, sizing, stop_loss=99.0)
sell_order = orchestrator.build_order(sell, sizing, stop_loss=101.0)
hold_order = orchestrator.build_order(hold, sizing, stop_loss=99.0)

assert isinstance(buy_order, OrderRequest)
assert buy_order.symbol == "TEST"
assert buy_order.side == "BUY"
assert buy_order.quantity == 5.0
assert buy_order.order_type == "MARKET"
assert buy_order.stop_loss == 99.0
assert isinstance(sell_order, OrderRequest)
assert sell_order.side == "SELL"
assert sell_order.quantity == 5.0
assert sell_order.stop_loss == 101.0
assert hold_order is None
print("ORCHESTRATOR_ORDER_CONSTRUCTION: PASS")