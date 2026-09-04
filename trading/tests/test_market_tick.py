from datetime import UTC, datetime
from trading.market.provider import MarketTick, MarketDataProvider

NOW = datetime.now(UTC)

def expect_rejection(tick):
    try:
        tick.validate()
    except ValueError:
        return True
    return False

assert MarketTick("TEST", 100, 101, NOW).validate() is True
assert expect_rejection(MarketTick("", 100, 101, NOW))
assert expect_rejection(MarketTick("TEST", 0, 101, NOW))
assert expect_rejection(MarketTick("TEST", 100, 0, NOW))
assert expect_rejection(MarketTick("TEST", 102, 101, NOW))
assert expect_rejection(MarketTick("TEST", 100, 101, datetime(2026, 1, 1)))

try:
    MarketDataProvider().get_tick("TEST")
except NotImplementedError:
    pass
else:
    raise AssertionError("base provider must remain unconfigured")

print("MARKET_TICK_CONTRACT_TESTS: PASS")
