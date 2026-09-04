from dataclasses import dataclass

@dataclass(frozen=True)
class PositionSizingInput:
    equity: float
    risk_fraction: float
    entry_price: float
    stop_price: float
    contract_multiplier: float = 1.0
    min_quantity: float = 0.0
    quantity_step: float = 1.0
    max_notional: float = 0.0

    def validate(self):
        if self.equity <= 0:
            raise ValueError("equity must be positive")
        if self.risk_fraction <= 0:
            raise ValueError("risk_fraction must be positive")
        if self.entry_price <= 0:
            raise ValueError("entry_price must be positive")
        if self.stop_price <= 0:
            raise ValueError("stop_price must be positive")
        if self.entry_price == self.stop_price:
            raise ValueError("entry_price and stop_price must differ")
        if self.contract_multiplier <= 0:
            raise ValueError("contract_multiplier must be positive")
        if self.min_quantity < 0:
            raise ValueError("min_quantity cannot be negative")
        if self.quantity_step <= 0:
            raise ValueError("quantity_step must be positive")
        if self.max_notional < 0:
            raise ValueError("max_notional cannot be negative")
        return True
