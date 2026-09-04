from dataclasses import dataclass

@dataclass(frozen=True)
class TradingConfig:
    environment: str = "paper"
    broker: str = "unset"
    account_currency: str = "USD"
    max_risk_per_trade: float = 0.01
    max_daily_loss: float = 0.03
    max_drawdown: float = 0.10
    allow_live_orders: bool = False

    def validate(self):
        if self.environment not in {"development", "paper", "live"}:
            raise ValueError("Invalid trading environment")
        if not 0 < self.max_risk_per_trade <= 0.05:
            raise ValueError("max_risk_per_trade must be > 0 and <= 0.05")
        if not 0 < self.max_daily_loss <= 0.20:
            raise ValueError("max_daily_loss must be > 0 and <= 0.20")
        if not 0 < self.max_drawdown <= 0.50:
            raise ValueError("max_drawdown must be > 0 and <= 0.50")
        if self.environment == "live" and not self.allow_live_orders:
            raise ValueError("Live environment requires explicit live-order permission")
        return True
