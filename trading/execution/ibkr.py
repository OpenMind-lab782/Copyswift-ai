import os

from trading.execution.broker import BrokerAdapter, OrderRequest, OrderResult

class IBKRBrokerAdapter(BrokerAdapter):
    def __init__(self, host=None, port=None, client_id=None):
        self.host = host or os.getenv("IBKR_HOST", "127.0.0.1")
        self.port = int(port or os.getenv("IBKR_PORT", "7497"))
        self.client_id = int(client_id or os.getenv("IBKR_CLIENT_ID", "1"))
        self.connected = False

    def connect(self) -> bool:
        raise NotImplementedError("IBKR transport is not configured yet")

    def get_account(self) -> dict:
        raise NotImplementedError("IBKR account transport is not configured yet")

    def place_order(self, order: OrderRequest) -> OrderResult:
        order.validate()
        raise NotImplementedError("IBKR order transport is not configured yet")

    def cancel_order(self, broker_order_id: str) -> OrderResult:
        raise NotImplementedError("IBKR order transport is not configured yet")
