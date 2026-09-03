from trading.execution.broker import BrokerAdapter, OrderRequest, OrderResult
from trading.market.provider import MarketDataProvider, MarketTick
class PaperBroker(BrokerAdapter):
    def __init__(self, initial_cash, market_data_provider=None):
        if initial_cash <= 0:
            raise ValueError("initial_cash must be positive")
        self.cash = float(initial_cash)
        if market_data_provider is not None and not isinstance(market_data_provider, MarketDataProvider):
            raise ValueError("market_data_provider must be a MarketDataProvider")
        self.market_data_provider = market_data_provider
        self.connected = False
        self._next_order_id = 1
        self._orders = {}

    def connect(self) -> bool:
        self.connected = True
        return True

    def get_account(self) -> dict:
        return {"cash": self.cash, "equity": self.cash}

    def place_order(self, order: OrderRequest, tick: MarketTick = None) -> OrderResult:
        if not self.connected:
            raise RuntimeError("paper broker is not connected")
        order.validate()
        if tick is None:
            if self.market_data_provider is None:
                raise ValueError("market_data_provider is required when tick is not provided")
            tick = self.market_data_provider.get_tick(order.symbol)
        tick.validate()
        if order.symbol != tick.symbol:
            raise ValueError("order symbol does not match market tick")
        if order.order_type.upper() != "MARKET":
            raise NotImplementedError("paper broker currently supports MARKET orders only")
        fill_price = tick.ask if order.side.upper() == "BUY" else tick.bid
        notional = fill_price * order.quantity
        if order.side.upper() == "BUY" and notional > self.cash:
            raise ValueError("insufficient paper cash")
        if order.side.upper() == "BUY":
            self.cash -= notional
        else:
            self.cash += notional
        broker_order_id = f"PAPER-{self._next_order_id}"
        self._orders[broker_order_id] = {"status": "FILLED", "order": order, "fill_price": fill_price, "notional": notional}
        self._next_order_id += 1
        return OrderResult(broker_order_id=broker_order_id, status="FILLED", raw={"symbol": order.symbol, "side": order.side.upper(), "quantity": order.quantity, "fill_price": fill_price, "notional": notional})

    def cancel_order(self, broker_order_id: str) -> OrderResult:
        if not self.connected:
            raise RuntimeError("paper broker is not connected")
        if broker_order_id not in self._orders:
            raise ValueError("unknown paper broker order")
        if self._orders[broker_order_id]["status"] == "FILLED":
            raise ValueError("filled paper orders cannot be cancelled")
        self._orders[broker_order_id]["status"] = "CANCELLED"
        return OrderResult(broker_order_id=broker_order_id, status="CANCELLED", raw=self._orders[broker_order_id])
