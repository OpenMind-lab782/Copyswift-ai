from dataclasses import dataclass
from datetime import datetime
from trading.portfolio.intent import PositionIntent
from trading.portfolio.ledger import Position, PositionLedger


@dataclass(frozen=True)
class ExecutionFill:
    symbol: str
    side: str
    quantity: float
    fill_price: float
    broker_order_id: str
    intent: PositionIntent
    timestamp: datetime
    fill_id: str = ""

    def validate(self):
        if not self.symbol.strip(): raise ValueError("symbol is required")
        if self.side.upper() not in {"BUY", "SELL"}: raise ValueError("side must be BUY or SELL")
        if self.quantity <= 0: raise ValueError("quantity must be positive")
        if self.fill_price <= 0: raise ValueError("fill_price must be positive")
        if not self.broker_order_id.strip(): raise ValueError("broker_order_id is required")
        if not isinstance(self.intent, PositionIntent): raise ValueError("intent must be a PositionIntent")
        if not isinstance(self.timestamp, datetime): raise ValueError("timestamp must be a datetime")
        if not isinstance(self.fill_id, str): raise ValueError("fill_id must be a string")
        if self.fill_id and not self.fill_id.strip(): raise ValueError("fill_id cannot be blank")
        return True


@dataclass(frozen=True)
class AccountingResult:
    broker_order_id: str
    intent: PositionIntent
    symbol: str
    side: str
    quantity: float
    fill_price: float
    realized_pnl: float = 0.0
    closed_quantity: float = 0.0


class PortfolioAccounting:
    def __init__(self, ledger=None):
        self.ledger = PositionLedger() if ledger is None else ledger
        if not isinstance(self.ledger, PositionLedger):
            raise ValueError("ledger must be a PositionLedger")
        self._applied_fill_keys = set()

    def apply_fill(self, fill):
        if not isinstance(fill, ExecutionFill):
            raise ValueError("fill must be an ExecutionFill")
        fill.validate()
        fill_key = ("FILL_ID", fill.broker_order_id, fill.fill_id) if fill.fill_id else ("LEGACY", fill.symbol, fill.side.upper(), fill.quantity, fill.fill_price, fill.broker_order_id, fill.intent, fill.timestamp)
        if fill_key in self._applied_fill_keys:
            raise ValueError("duplicate fill rejected")
        intent = fill.intent
        side = fill.side.upper()
        expected_side = {
            PositionIntent.OPEN_LONG: "BUY",
            PositionIntent.CLOSE_LONG: "SELL",
            PositionIntent.OPEN_SHORT: "SELL",
            PositionIntent.CLOSE_SHORT: "BUY",
        }[intent]
        if side != expected_side:
            raise ValueError(f"{intent.value} requires {expected_side} side")
        if intent == PositionIntent.OPEN_LONG:
            self.ledger.open_position(Position(fill.symbol, "LONG", fill.quantity, fill.fill_price, fill.timestamp, broker_order_id=fill.broker_order_id))
            self._applied_fill_keys.add(fill_key)
            return AccountingResult(fill.broker_order_id, intent, fill.symbol, side, fill.quantity, fill.fill_price)
        if intent == PositionIntent.OPEN_SHORT:
            self.ledger.open_position(Position(fill.symbol, "SHORT", fill.quantity, fill.fill_price, fill.timestamp, broker_order_id=fill.broker_order_id))
            self._applied_fill_keys.add(fill_key)
            return AccountingResult(fill.broker_order_id, intent, fill.symbol, side, fill.quantity, fill.fill_price)
        ledger_side = "LONG" if intent == PositionIntent.CLOSE_LONG else "SHORT"
        result = self.ledger.close_position(fill.symbol, ledger_side, fill.quantity, fill.fill_price)
        self._applied_fill_keys.add(fill_key)
        return AccountingResult(fill.broker_order_id, intent, fill.symbol, side, fill.quantity, fill.fill_price, result.realized_pnl, result.closed_quantity)


def fill_from_order_result(order_result, intent, timestamp):
    from trading.execution.broker import OrderResult
    if not isinstance(order_result, OrderResult):
        raise ValueError("order_result must be an OrderResult")
    if order_result.status.upper() != "FILLED":
        raise ValueError("order_result must be FILLED")
    raw = order_result.raw or {}
    symbol = raw.get("symbol")
    side = raw.get("side")
    quantity = raw.get("filled_quantity", raw.get("quantity"))
    fill_price = raw.get("fill_price", raw.get("price"))
    fill_id = raw.get("fill_id", raw.get("execution_id", ""))
    return ExecutionFill(symbol, side, quantity, fill_price, order_result.broker_order_id, intent, timestamp, fill_id)


def account_submitted_order(order_request, order_result, timestamp, accounting):
    from trading.execution.broker import OrderRequest
    if not isinstance(order_request, OrderRequest):
        raise ValueError("order_request must be an OrderRequest")
    order_request.validate()
    if order_request.intent is None:
        raise ValueError("order_request intent is required")
    fill = fill_from_order_result(order_result, order_request.intent, timestamp)
    if fill.symbol != order_request.symbol:
        raise ValueError("filled symbol does not match submitted order")
    if fill.side.upper() != order_request.side.upper():
        raise ValueError("filled side does not match submitted order")
    if fill.quantity > order_request.quantity:
        raise ValueError("filled quantity exceeds submitted quantity")
    return accounting.apply_fill(fill)


def account_filled_order(order_result, intent, timestamp, accounting):
    if not isinstance(accounting, PortfolioAccounting):
        raise ValueError("accounting must be a PortfolioAccounting")
    fill = fill_from_order_result(order_result, intent, timestamp)
    return accounting.apply_fill(fill)
