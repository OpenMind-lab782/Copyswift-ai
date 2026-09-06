from datetime import datetime, timezone
from trading.execution.broker import OrderRequest, OrderResult
from trading.portfolio.accounting import PortfolioAccounting, account_filled_order
from trading.portfolio.intent import PositionIntent

class FakeBroker:
    def place_order(self, order):
        order.validate()
        return OrderResult("BROKER-001", "FILLED", {"symbol": order.symbol, "side": order.side, "quantity": order.quantity, "filled_quantity": order.quantity, "price": 100.0, "fill_price": 100.0})

accounting = PortfolioAccounting()
broker = FakeBroker()
ts = datetime.now(timezone.utc)

open_order = OrderRequest("TEST", "BUY", 5.0, intent=PositionIntent.OPEN_LONG)
open_result = broker.place_order(open_order)
open_result_accounted = account_filled_order(open_result, open_order.intent, ts, accounting)
assert open_result_accounted.intent == PositionIntent.OPEN_LONG
assert accounting.ledger.get_inventory("TEST", "LONG") == 5.0

close_order = OrderRequest("TEST", "SELL", 2.0, intent=PositionIntent.CLOSE_LONG)
close_result = OrderResult("BROKER-002", "FILLED", {"symbol": "TEST", "side": "SELL", "quantity": 2.0, "filled_quantity": 2.0, "price": 105.0, "fill_price": 105.0})
close_accounted = account_filled_order(close_result, close_order.intent, ts, accounting)
assert close_accounted.intent == PositionIntent.CLOSE_LONG
assert close_accounted.realized_pnl == 10.0
assert accounting.ledger.get_inventory("TEST", "LONG") == 3.0

try:
    account_filled_order(open_result, None, ts, accounting)
except ValueError:
    pass
else:
    raise AssertionError("missing intent must be rejected")

assert accounting.ledger.get_inventory("TEST", "SHORT") == 0.0
print("EXECUTION_ACCOUNTING_BOUNDARY: PASS")

from trading.portfolio.accounting import account_submitted_order

accounting2 = PortfolioAccounting()
submitted = OrderRequest('BOUNDARY', 'BUY', 4.0, intent=PositionIntent.OPEN_LONG)
filled = OrderResult('BROKER-003', 'FILLED', {'symbol': 'BOUNDARY', 'side': 'BUY', 'quantity': 4.0, 'filled_quantity': 4.0, 'fill_price': 200.0})
result = account_submitted_order(submitted, filled, ts, accounting2)
assert result.intent == PositionIntent.OPEN_LONG
assert accounting2.ledger.get_inventory('BOUNDARY', 'LONG') == 4.0

partial = OrderRequest('PARTIAL', 'BUY', 5.0, intent=PositionIntent.OPEN_LONG)
partial_fill = OrderResult('BROKER-004', 'FILLED', {'symbol': 'PARTIAL', 'side': 'BUY', 'quantity': 5.0, 'filled_quantity': 2.0, 'fill_price': 50.0})
account_submitted_order(partial, partial_fill, ts, accounting2)
assert accounting2.ledger.get_inventory('PARTIAL', 'LONG') == 2.0

try:
    account_submitted_order(OrderRequest('NOINTENT', 'BUY', 1.0), filled, ts, accounting2)
except ValueError:
    pass
else:
    raise AssertionError('missing submitted intent must be rejected')

mismatch = OrderResult('BROKER-005', 'FILLED', {'symbol': 'WRONG', 'side': 'BUY', 'quantity': 1.0, 'filled_quantity': 1.0, 'fill_price': 50.0})
try:
    account_submitted_order(OrderRequest('EXPECTED', 'BUY', 1.0, intent=PositionIntent.OPEN_LONG), mismatch, ts, accounting2)
except ValueError:
    pass
else:
    raise AssertionError('symbol mismatch must be rejected')

print('SUBMITTED_ORDER_ACCOUNTING: PASS')
