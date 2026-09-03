from dataclasses import dataclass

@dataclass(frozen=True)
class TradingSignal:
    symbol: str
    action: str
    confidence: float
    price: float
    reason: str

    def validate(self):
        if not self.symbol.strip():
            raise ValueError("symbol is required")
        if self.action.upper() not in {"BUY", "SELL", "HOLD"}:
            raise ValueError("action must be BUY, SELL or HOLD")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.price <= 0:
            raise ValueError("price must be positive")
        if not self.reason.strip():
            raise ValueError("reason is required")
        return True
