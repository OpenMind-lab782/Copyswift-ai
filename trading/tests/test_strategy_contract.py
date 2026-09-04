from datetime import UTC, datetime, timedelta
from trading.market.provider import MarketTick
from trading.strategies.signal import TradingSignal
from trading.strategies.momentum import MomentumStrategy

def ticks(prices):
    base = datetime.now(UTC)
    return [MarketTick("TEST", p, p, base + timedelta(seconds=i)) for i, p in enumerate(prices)]

def expect_rejection(fn):
    try:
        fn()
    except ValueError:
        return True
    return False

assert expect_rejection(lambda: MomentumStrategy(lookback=1))
assert expect_rejection(lambda: MomentumStrategy(min_move=-0.1))
assert expect_rejection(lambda: MomentumStrategy(lookback=5).evaluate(ticks([100, 101, 102])))

buy = MomentumStrategy(lookback=3, min_move=0.005).evaluate(ticks([100, 101, 102]))
assert buy.action == "BUY"
assert buy.confidence == 1.0
assert buy.validate() is True

sell = MomentumStrategy(lookback=3, min_move=0.005).evaluate(ticks([102, 101, 100]))
assert sell.action == "SELL"
assert sell.confidence == 1.0
assert sell.validate() is True

hold = MomentumStrategy(lookback=3, min_move=0.005).evaluate(ticks([100, 100.1, 100.2]))
assert hold.action == "HOLD"
assert hold.confidence == 0.0
assert hold.validate() is True

assert expect_rejection(lambda: TradingSignal("", "BUY", 0.5, 100, "x").validate())
assert expect_rejection(lambda: TradingSignal("TEST", "BAD", 0.5, 100, "x").validate())
assert expect_rejection(lambda: TradingSignal("TEST", "BUY", 1.1, 100, "x").validate())
assert expect_rejection(lambda: TradingSignal("TEST", "BUY", 0.5, 0, "x").validate())
assert expect_rejection(lambda: TradingSignal("TEST", "BUY", 0.5, 100, "").validate())
print("STRATEGY_CONTRACT_TESTS: PASS")
