from trading.execution.broker import OrderRequest, BrokerAdapter

def expect_rejection(order):
    try:
        order.validate()
    except ValueError:
        return True
    return False

assert OrderRequest("TEST", "BUY", 10).validate() is True
assert OrderRequest("TEST", "SELL", 10).validate() is True
assert OrderRequest("TEST", "BUY", 10, "LIMIT", 100).validate() is True
assert expect_rejection(OrderRequest("", "BUY", 10))
assert expect_rejection(OrderRequest("TEST", "BAD", 10))
assert expect_rejection(OrderRequest("TEST", "BUY", 0))
assert expect_rejection(OrderRequest("TEST", "BUY", -1))
assert expect_rejection(OrderRequest("TEST", "BUY", 10, "STOP"))
assert expect_rejection(OrderRequest("TEST", "BUY", 10, "LIMIT"))
assert expect_rejection(OrderRequest("TEST", "BUY", 10, "LIMIT", 0))

try:
    BrokerAdapter().place_order(OrderRequest("TEST", "BUY", 1))
except NotImplementedError:
    pass
else:
    raise AssertionError("base broker must remain unconfigured")

print("EXECUTION_CONTRACT_TESTS: PASS")

from trading.portfolio.intent import PositionIntent

assert OrderRequest("TEST", "BUY", 10, intent=PositionIntent.OPEN_LONG).validate() is True
assert OrderRequest("TEST", "SELL", 10, intent=PositionIntent.CLOSE_LONG).validate() is True
assert OrderRequest("TEST", "SELL", 10, intent=PositionIntent.OPEN_SHORT).validate() is True
assert OrderRequest("TEST", "BUY", 10, intent=PositionIntent.CLOSE_SHORT).validate() is True
assert expect_rejection(OrderRequest("TEST", "BUY", 10, intent="BAD_INTENT"))
assert expect_rejection(OrderRequest(123, "BUY", 1))
assert expect_rejection(OrderRequest("BTC", 123, 1))
assert expect_rejection(OrderRequest("BTC", "BUY", True))
assert expect_rejection(OrderRequest("BTC", "BUY", float("nan")))
assert expect_rejection(OrderRequest("BTC", "BUY", float("inf")))
assert expect_rejection(OrderRequest("BTC", "BUY", 1, order_type=123))
assert expect_rejection(OrderRequest("BTC", "BUY", 1, limit_price=True))
assert expect_rejection(OrderRequest("BTC", "BUY", 1, limit_price=float("nan")))
assert expect_rejection(OrderRequest("BTC", "BUY", 1, limit_price=float("inf")))
assert expect_rejection(OrderRequest("BTC", "BUY", 1, order_type="LIMIT"))
print("ORDER_REQUEST_MALFORMED_INPUT_TESTS: PASS")
print("EXPLICIT_POSITION_INTENT_TESTS: PASS")
