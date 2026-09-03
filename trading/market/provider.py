from dataclasses import dataclass
from datetime import UTC, datetime

@dataclass(frozen=True)
class MarketTick:
    symbol: str
    bid: float
    ask: float
    timestamp: datetime

    def validate(self):
        if not self.symbol.strip():
            raise ValueError("symbol is required")
        if self.bid <= 0 or self.ask <= 0:
            raise ValueError("bid and ask must be positive")
        if self.ask < self.bid:
            raise ValueError("ask cannot be below bid")
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return True

class MarketDataProvider:
    def get_tick(self, symbol: str) -> MarketTick:
        raise NotImplementedError("Market data provider is not configured")
