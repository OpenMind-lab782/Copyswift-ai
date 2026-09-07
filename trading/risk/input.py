from dataclasses import dataclass
from trading.risk.numeric import validate_risk_number

@dataclass(frozen=True)
class RiskInput:
    equity: float
    starting_daily_equity: float
    peak_equity: float
    proposed_risk_fraction: float
    proposed_notional: float
    open_risk_fraction: float
    open_notional_fraction: float
    trades_last_minute: int
    duplicate: bool = False
    stale_market_data: bool = False
    price_valid: bool = True
    broker_state_known: bool = True
    kill_switch: bool = False

    def validate(self):
        validate_risk_number(self.equity)
        validate_risk_number(self.starting_daily_equity)
        validate_risk_number(self.peak_equity)
        validate_risk_number(self.proposed_risk_fraction)
        validate_risk_number(self.proposed_notional)
        validate_risk_number(self.open_risk_fraction)
        validate_risk_number(self.open_notional_fraction)
        if isinstance(self.trades_last_minute, bool) or not isinstance(self.trades_last_minute, int):
            raise ValueError("trades_last_minute must be an integer")
        for flag in (self.duplicate, self.stale_market_data, self.price_valid, self.broker_state_known, self.kill_switch):
            if not isinstance(flag, bool):
                raise ValueError("risk flags must be boolean")
        if self.equity <= 0:
            raise ValueError("equity must be positive")
        if self.starting_daily_equity <= 0:
            raise ValueError("starting_daily_equity must be positive")
        if self.peak_equity <= 0:
            raise ValueError("peak_equity must be positive")
        if self.proposed_risk_fraction < 0:
            raise ValueError("proposed_risk_fraction cannot be negative")
        if self.proposed_notional < 0:
            raise ValueError("proposed_notional cannot be negative")
        if self.open_risk_fraction < 0:
            raise ValueError("open_risk_fraction cannot be negative")
        if self.open_notional_fraction < 0:
            raise ValueError("open_notional_fraction cannot be negative")
        if self.trades_last_minute < 0:
            raise ValueError("trades_last_minute cannot be negative")
        return True
