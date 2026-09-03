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

    def validate(self):
        if not self.symbol.strip():
            raise ValueError("symbol is required")
        if self.side.upper() not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.order_type.upper() not in {"MARKET", "LIMIT"}:
            raise ValueError("unsupported order type")
        if self.order_type.upper() == "LIMIT" and (self.limit_price is None or self.limit_price <= 0):
            raise ValueError("limit orders require a positive limit_price")
        return True

@dataclass(frozen=True)
class OrderResult:
    broker_order_id: str
    status: str
    raw: dict[str, Any]

class BrokerAdapter:
    def connect(self) -> bool:
        raise NotImplementedError

    def get_account(self) -> dict[str, Any]:
        raise NotImplementedError

    def place_order(self, order: OrderRequest) -> OrderResult:
        raise NotImplementedError

    def cancel_order(self, broker_order_id: str) -> OrderResult:
        raise NotImplementedError
