from dataclasses import dataclass

@dataclass(frozen=True)
class RiskPolicy:
    max_risk_per_trade: float = 0.01
    max_daily_loss: float = 0.03
    max_drawdown: float = 0.10
    max_open_risk: float = 0.03
    max_open_notional_fraction: float = 1.0
    max_trades_per_minute: int = 5
    duplicate_window_seconds: float = 60.0

    def validate(self):
        if not 0 < self.max_risk_per_trade <= 0.05:
            raise ValueError("max_risk_per_trade must be > 0 and <= 0.05")
        if not 0 < self.max_daily_loss <= 0.20:
            raise ValueError("max_daily_loss must be > 0 and <= 0.20")
        if not 0 < self.max_drawdown <= 0.50:
            raise ValueError("max_drawdown must be > 0 and <= 0.50")
        if not 0 < self.max_open_risk <= 0.50:
            raise ValueError("max_open_risk must be > 0 and <= 0.50")
        if not 0 < self.max_open_notional_fraction <= 1.0:
            raise ValueError("max_open_notional_fraction must be > 0 and <= 1.0")
        if self.max_trades_per_minute < 1:
            raise ValueError("max_trades_per_minute must be at least 1")
        if self.duplicate_window_seconds <= 0:
            raise ValueError("duplicate_window_seconds must be positive")
        return True
