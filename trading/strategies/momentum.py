from trading.market.provider import MarketTick
from trading.strategies.signal import TradingSignal

class MomentumStrategy:
    def __init__(self, lookback: int = 20, min_move: float = 0.0005):
        if lookback < 2:
            raise ValueError("lookback must be at least 2")
        if min_move < 0:
            raise ValueError("min_move must be non-negative")
        self.lookback = lookback
        self.min_move = min_move

    def evaluate(self, ticks: list[MarketTick]) -> TradingSignal:
        if len(ticks) < self.lookback:
            raise ValueError(f"at least {self.lookback} ticks are required")
        recent = ticks[-self.lookback:]
        for tick in recent:
            tick.validate()
        first = recent[0].bid
        last = recent[-1].bid
        movement = (last - first) / first
        if movement > self.min_move:
            action = "BUY"
        elif movement < -self.min_move:
            action = "SELL"
        else:
            action = "HOLD"
        confidence = min(1.0, abs(movement) / max(self.min_move, 1e-12)) if action != "HOLD" else 0.0
        signal = TradingSignal(symbol=recent[-1].symbol, action=action, confidence=confidence, price=last, reason=f"momentum={movement:.6f}")
        signal.validate()
        return signal
