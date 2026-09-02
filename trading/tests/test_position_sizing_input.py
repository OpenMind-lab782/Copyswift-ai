from trading.risk.sizing import PositionSizingInput

BASE = dict(equity=10000, risk_fraction=0.01, entry_price=100, stop_price=98, contract_multiplier=1, min_quantity=0, quantity_step=1, max_notional=0)

def expect_rejection(overrides):
    values = BASE.copy(); values.update(overrides)
    try:
        PositionSizingInput(**values).validate()
    except ValueError:
        return True
    return False

assert PositionSizingInput(**BASE).validate() is True
assert expect_rejection({"equity": 0})
assert expect_rejection({"risk_fraction": 0})
assert expect_rejection({"entry_price": 0})
assert expect_rejection({"stop_price": 0})
assert expect_rejection({"entry_price": 100, "stop_price": 100})
assert expect_rejection({"contract_multiplier": 0})
assert expect_rejection({"min_quantity": -1})
assert expect_rejection({"quantity_step": 0})
assert expect_rejection({"max_notional": -1})
print("POSITION_SIZING_INPUT_TESTS: PASS")
