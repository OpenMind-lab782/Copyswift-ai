from datetime import UTC, datetime
from trading.execution.broker import BrokerAdapter, OrderRequest
from trading.execution.paper import PaperBroker
from trading.market.provider import MarketTick

tick = MarketTick("TEST", 99.0, 101.0, datetime.now(UTC))
broker = PaperBroker(initial_cash=10000.0)

assert isinstance(broker, BrokerAdapter)
assert broker.get_account()["cash"] == 10000.0
assert broker.get_account()["equity"] == 10000.0

assert broker.connect() is True

buy = broker.place_order(OrderRequest("TEST", "BUY", 10), tick)
assert buy.status == "FILLED"
assert buy.broker_order_id
assert buy.raw["symbol"] == "TEST"
assert buy.raw["side"] == "BUY"
assert buy.raw["fill_price"] == 101.0
assert buy.raw["quantity"] == 10.0

sell = broker.place_order(OrderRequest("TEST", "SELL", 5), tick)
assert sell.status == "FILLED"
assert sell.raw["fill_price"] == 99.0

ok = False
try:
    broker.cancel_order(buy.broker_order_id)
except ValueError as e:
    ok = str(e) == "filled paper orders cannot be cancelled"
assert ok


print("PAPER_BROKER_CONTRACT_TESTS: PASS")


result_ok = broker.get_account()
assert result_ok["cash"] == 9485.0
assert buy.raw["fill_id"] == buy.broker_order_id
assert sell.raw["fill_id"] == sell.broker_order_id
assert buy.broker_order_id != sell.broker_order_id

from trading.execution.broker import OrderResult
assert OrderResult("ORDER-1", "FILLED", {}).validate() is True

for bad_result in [OrderResult("", "FILLED", {}), OrderResult("ORDER-2", "", {}), OrderResult("ORDER-3", "FILLED", None)]:
    try:
        bad_result.validate()
    except ValueError:
        pass
    else:
        raise AssertionError("invalid OrderResult accepted")

print("ORDER_RESULT_CONTRACT_TESTS: PASS")
