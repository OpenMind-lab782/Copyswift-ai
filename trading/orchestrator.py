from trading.risk.input import RiskInput
from trading.strategies.signal import TradingSignal

class TradingOrchestrator:
    def __init__(self, risk_engine):
        if risk_engine is None:
            raise ValueError("risk_engine is required")
        self.risk_engine = risk_engine

    def evaluate_signal(self, signal):
        if not isinstance(signal, TradingSignal):
            raise ValueError("signal must be a TradingSignal")
        signal.validate()
        if signal.action.upper() == "HOLD":
            return None
        return signal

    def evaluate_risk(self, state, proposed_risk_fraction, proposed_notional, now=None, order_key=None):
        risk_input = self.build_risk_input(state, proposed_risk_fraction, proposed_notional, now, order_key)
        return self.risk_engine.evaluate(risk_input)

    def build_risk_input(self, state, proposed_risk_fraction, proposed_notional, now=None, order_key=None):
        state.validate()
        if proposed_risk_fraction < 0:
            raise ValueError("proposed_risk_fraction cannot be negative")
        if proposed_notional < 0:
            raise ValueError("proposed_notional cannot be negative")
        import time
        current_time = time.time() if now is None else now
        trades_last_minute = sum(1 for timestamp in state.recent_trade_times if current_time - timestamp < 60)
        duplicate = False
        if order_key is not None and order_key in state.recent_order_keys:
            duplicate = current_time - state.recent_order_keys[order_key] < self.risk_engine.policy.duplicate_window_seconds
        return RiskInput(equity=state.equity, starting_daily_equity=state.starting_daily_equity, peak_equity=state.peak_equity, proposed_risk_fraction=proposed_risk_fraction, proposed_notional=proposed_notional, open_risk_fraction=state.open_risk / state.equity, open_notional_fraction=state.open_notional / state.equity, trades_last_minute=trades_last_minute, duplicate=duplicate, kill_switch=state.kill_switch)

    def build_order_key(self, symbol, side, quantity, entry_price):
        return f"{symbol}|{side.upper()}|{quantity}|{entry_price}"
