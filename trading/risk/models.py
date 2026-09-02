from dataclasses import dataclass, field

@dataclass(frozen=True)
class RiskDecision:
    action: str
    approved_quantity: float
    risk_amount: float
    reasons: tuple[str, ...] = field(default_factory=tuple)

    def validate(self):
        if self.action not in {"ALLOW", "REDUCE", "REJECT"}:
            raise ValueError("action must be ALLOW, REDUCE or REJECT")
        if self.approved_quantity < 0:
            raise ValueError("approved_quantity cannot be negative")
        if self.risk_amount < 0:
            raise ValueError("risk_amount cannot be negative")
        if not self.reasons:
            raise ValueError("at least one risk decision reason is required")
        if self.action == "REJECT" and self.approved_quantity != 0:
            raise ValueError("rejected decisions cannot approve quantity")
        if self.action == "ALLOW" and self.approved_quantity <= 0:
            raise ValueError("allowed decisions require positive quantity")
        return True
