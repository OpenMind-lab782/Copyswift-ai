from dataclasses import dataclass, field

@dataclass
class RiskState:
    equity: float
    starting_daily_equity: float
    peak_equity: float
    realized_pnl: float = 0.0
    open_risk: float = 0.0
    open_notional: float = 0.0
    recent_trade_times: list[float] = field(default_factory=list)
    recent_order_keys: dict[str, float] = field(default_factory=dict)
    kill_switch: bool = False

    def validate(self):
        if self.equity <= 0:
            raise ValueError("equity must be positive")
        if self.starting_daily_equity <= 0:
            raise ValueError("starting_daily_equity must be positive")
        if self.peak_equity <= 0:
            raise ValueError("peak_equity must be positive")
        if self.open_risk < 0:
            raise ValueError("open_risk cannot be negative")
        if self.open_notional < 0:
            raise ValueError("open_notional cannot be negative")
        return True
