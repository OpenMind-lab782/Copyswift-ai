from trading.portfolio.intent import PositionIntent
import math
from dataclasses import dataclass

from typing import Any

@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    side: str
    quantity: float
    order_type: str = "MARKET"
    limit_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    intent: PositionIntent | None = None

    def validate(self):
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("symbol is required")
        if not isinstance(self.side, str) or self.side.upper() not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        if not isinstance(self.quantity, (int, float)) or isinstance(self.quantity, bool) or not math.isfinite(self.quantity) or self.quantity <= 0:
            raise ValueError("quantity must be positive and finite")
        if self.intent is not None and not isinstance(self.intent, PositionIntent):
            raise ValueError("intent must be a PositionIntent")
        if not isinstance(self.order_type, str) or self.order_type.upper() not in {"MARKET", "LIMIT"}:
            raise ValueError("unsupported order type")
        if self.limit_price is not None and (not isinstance(self.limit_price, (int, float)) or isinstance(self.limit_price, bool) or not math.isfinite(self.limit_price) or self.limit_price <= 0):
            raise ValueError("limit_price must be positive and finite")
        if self.order_type.upper() == "LIMIT" and self.limit_price is None:
            raise ValueError("limit orders require a positive limit_price")
        return True

@dataclass(frozen=True)
class OrderResult:
    broker_order_id: str
    status: str
    raw: dict[str, Any]

    def validate(self):
        if not isinstance(self.broker_order_id, str) or not self.broker_order_id.strip(): raise ValueError("broker_order_id is required")
        if not isinstance(self.status, str) or not self.status.strip(): raise ValueError("status is required")
        if not isinstance(self.raw, dict): raise ValueError("raw must be a dict")
        return True

class BrokerAdapter:
    def connect(self) -> bool:
        raise NotImplementedError

    def get_account(self) -> dict[str, Any]:
        raise NotImplementedError

    def place_order(self, order: OrderRequest) -> OrderResult:
        raise NotImplementedError

    def cancel_order(self, broker_order_id: str) -> OrderResult:
        raise NotImplementedError
