from trading.risk.numeric import normalize_risk, risk_decimal
from trading.risk.sizing import PositionSizingInput

class PositionSizer:
    def calculate(self, sizing_input: PositionSizingInput) -> dict:
        sizing_input.validate()
        equity = risk_decimal(sizing_input.equity)
        risk_budget = equity * risk_decimal(sizing_input.risk_fraction)
        price_distance = abs(risk_decimal(sizing_input.entry_price) - risk_decimal(sizing_input.stop_price))
        multiplier = risk_decimal(sizing_input.contract_multiplier)
        risk_per_unit = price_distance * multiplier
        if risk_per_unit <= 0:
            raise ValueError("risk per unit must be positive")
        raw_quantity = risk_budget / risk_per_unit
        step = risk_decimal(sizing_input.quantity_step)
        quantity = (raw_quantity // step) * step
        if sizing_input.min_quantity > 0 and quantity < risk_decimal(sizing_input.min_quantity):
            quantity = risk_decimal("0")
        notional = quantity * risk_decimal(sizing_input.entry_price) * multiplier
        max_notional = risk_decimal(sizing_input.max_notional)
        if max_notional > 0 and notional > max_notional:
            quantity = (max_notional / (risk_decimal(sizing_input.entry_price) * multiplier) // step) * step
            notional = quantity * risk_decimal(sizing_input.entry_price) * multiplier
        estimated_risk = quantity * risk_per_unit
        return {"quantity": float(normalize_risk(quantity)), "notional": float(normalize_risk(notional)), "risk_amount": float(normalize_risk(estimated_risk)), "risk_fraction": float(normalize_risk(estimated_risk / equity))}
