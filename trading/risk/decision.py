from dataclasses import dataclass

@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    action: str
    reason_code: str
    reason: str
    risk_fraction: float = 0.0
    approved_notional: float = 0.0

    def validate(self):
        if self.action.upper() not in {"ALLOW", "REDUCE", "REJECT"}:
            raise ValueError("action must be ALLOW, REDUCE or REJECT")
        if not self.reason_code.strip():
            raise ValueError("reason_code is required")
        if not self.reason.strip():
            raise ValueError("reason is required")
        if self.risk_fraction < 0:
            raise ValueError("risk_fraction cannot be negative")
        if self.approved_notional < 0:
            raise ValueError("approved_notional cannot be negative")
        if self.action.upper() == "ALLOW" and not self.allowed:
            raise ValueError("ALLOW decision must have allowed=True")
        if self.action.upper() == "REJECT" and self.allowed:
            raise ValueError("REJECT decision must have allowed=False")
        return True
