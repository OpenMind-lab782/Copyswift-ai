from trading.risk.decision import RiskDecision
from trading.risk.input import RiskInput
from trading.risk.policy import RiskPolicy
from trading.risk.numeric import normalize_risk, risk_decimal

class RiskEngine:
    def __init__(self, policy: RiskPolicy):
        policy.validate()
        self.policy = policy

    def evaluate(self, risk_input: RiskInput) -> RiskDecision:
        if not isinstance(risk_input, RiskInput):
            return RiskDecision(False, "REJECT", "INVALID_RISK_INPUT", "risk_input must be a RiskInput")
        try:
            risk_input.validate()
        except ValueError as exc:
            return RiskDecision(False, "REJECT", "INVALID_RISK_INPUT", str(exc))
        if risk_input.kill_switch:
            return RiskDecision(False, "REJECT", "KILL_SWITCH_ACTIVE", "Trading is blocked by the kill switch")
        if not risk_input.broker_state_known:
            return RiskDecision(False, "REJECT", "BROKER_STATE_UNKNOWN", "Broker/account state is unknown")
        if risk_input.stale_market_data:
            return RiskDecision(False, "REJECT", "STALE_MARKET_DATA", "Market data is stale")
        if not risk_input.price_valid:
            return RiskDecision(False, "REJECT", "INVALID_PRICE", "Proposed trade price is invalid")
        daily_loss = max(risk_decimal("0"), (risk_decimal(risk_input.starting_daily_equity) - risk_decimal(risk_input.equity)) / risk_decimal(risk_input.starting_daily_equity))
        if daily_loss >= risk_decimal(self.policy.max_daily_loss):
            return RiskDecision(False, "REJECT", "DAILY_LOSS_LIMIT", "Maximum daily loss limit reached")
        drawdown = max(risk_decimal("0"), (risk_decimal(risk_input.peak_equity) - risk_decimal(risk_input.equity)) / risk_decimal(risk_input.peak_equity))
        if drawdown >= risk_decimal(self.policy.max_drawdown):
            return RiskDecision(False, "REJECT", "MAX_DRAWDOWN", "Maximum drawdown limit reached")
        if risk_decimal(risk_input.proposed_risk_fraction) > risk_decimal(self.policy.max_risk_per_trade):
            return RiskDecision(False, "REDUCE", "TRADE_RISK_LIMIT", "Proposed trade risk exceeds the per-trade limit", self.policy.max_risk_per_trade)
        open_risk_total = risk_decimal(risk_input.open_risk_fraction) + risk_decimal(risk_input.proposed_risk_fraction)
        if open_risk_total > risk_decimal(self.policy.max_open_risk):
            remaining_risk = normalize_risk(normalize_risk(self.policy.max_open_risk) - normalize_risk(risk_input.open_risk_fraction))
            return RiskDecision(False, "REDUCE", "OPEN_RISK_LIMIT", "Aggregate open risk would exceed the configured limit", float(remaining_risk))
        proposed_notional_fraction = risk_decimal(risk_input.proposed_notional) / risk_decimal(risk_input.equity)
        open_notional_total = risk_decimal(risk_input.open_notional_fraction) + proposed_notional_fraction
        if open_notional_total > risk_decimal(self.policy.max_open_notional_fraction):
            return RiskDecision(False, "REDUCE", "OPEN_NOTIONAL_LIMIT", "Aggregate open notional would exceed the configured limit")
        if risk_input.trades_last_minute >= self.policy.max_trades_per_minute:
            return RiskDecision(False, "REJECT", "TRADE_RATE_LIMIT", "Maximum trade rate reached")
        if risk_input.duplicate:
            return RiskDecision(False, "REJECT", "DUPLICATE_ORDER", "Duplicate order detected")
        return RiskDecision(True, "ALLOW", "RISK_CHECK_PASSED", "All configured pre-trade risk checks passed", risk_input.proposed_risk_fraction, risk_input.proposed_notional)
