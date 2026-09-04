from trading.config.settings import TradingConfig

assert TradingConfig().validate() is True
assert TradingConfig(environment="development").validate() is True
assert TradingConfig(environment="paper").validate() is True
assert TradingConfig(environment="live", allow_live_orders=True).validate() is True

def expect_rejection(config):
    try:
        config.validate()
    except ValueError:
        return True
    return False

assert expect_rejection(TradingConfig(environment="invalid"))
assert expect_rejection(TradingConfig(environment="live", allow_live_orders=False))
assert expect_rejection(TradingConfig(max_risk_per_trade=0))
assert expect_rejection(TradingConfig(max_risk_per_trade=0.051))
assert expect_rejection(TradingConfig(max_daily_loss=0))
assert expect_rejection(TradingConfig(max_daily_loss=0.201))
assert expect_rejection(TradingConfig(max_drawdown=0))
assert expect_rejection(TradingConfig(max_drawdown=0.501))
print("TRADING_CONFIG_TESTS: PASS")
