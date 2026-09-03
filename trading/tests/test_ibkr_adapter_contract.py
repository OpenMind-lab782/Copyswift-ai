from trading.execution.broker import BrokerAdapter, OrderRequest
from trading.execution.ibkr import IBKRBrokerAdapter

broker = IBKRBrokerAdapter()
assert isinstance(broker, BrokerAdapter)
assert broker.connected is False
assert broker.host == "127.0.0.1"
assert broker.port == 7497
assert broker.client_id == 1

try:
    broker.connect()
except NotImplementedError:
    pass
else:
    raise AssertionError("IBKR transport must remain unconfigured")

try:
    broker.place_order(OrderRequest("TEST", "BUY", 1))
except NotImplementedError:
    pass
else:
    raise AssertionError("IBKR order transport must remain unconfigured")

print("IBKR_ADAPTER_CONTRACT_TESTS: PASS")
