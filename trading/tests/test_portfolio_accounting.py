from datetime import UTC, datetime

from trading.portfolio.accounting import ExecutionFill, PositionIntent


def test_position_intents():
    assert PositionIntent.OPEN_LONG.value == "OPEN_LONG"
    assert PositionIntent.CLOSE_LONG.value == "CLOSE_LONG"
    assert PositionIntent.OPEN_SHORT.value == "OPEN_SHORT"
    assert PositionIntent.CLOSE_SHORT.value == "CLOSE_SHORT"


def test_valid_execution_fill():
    fill = ExecutionFill("AAPL", "BUY", 10, 150.0, "ORDER-1", PositionIntent.OPEN_LONG, datetime.now(UTC))
    assert fill.validate() is True


def test_execution_fill_is_immutable():
    fill = ExecutionFill("AAPL", "BUY", 10, 150.0, "ORDER-1", PositionIntent.OPEN_LONG, datetime.now(UTC))
    try:
        fill.quantity = 20
        assert False
    except AttributeError:
        pass


def test_invalid_side_rejected():
    fill = ExecutionFill("AAPL", "HOLD", 10, 150.0, "ORDER-1", PositionIntent.OPEN_LONG, datetime.now(UTC))
    try:
        fill.validate()
        assert False
    except ValueError as exc:
        assert str(exc) == "side must be BUY or SELL"


def test_invalid_quantity_rejected():
    fill = ExecutionFill("AAPL", "BUY", 0, 150.0, "ORDER-1", PositionIntent.OPEN_LONG, datetime.now(UTC))
    try:
        fill.validate()
        assert False
    except ValueError as exc:
        assert str(exc) == "quantity must be positive"


def test_invalid_price_rejected():
    fill = ExecutionFill("AAPL", "BUY", 10, 0, "ORDER-1", PositionIntent.OPEN_LONG, datetime.now(UTC))
    try:
        fill.validate()
        assert False
    except ValueError as exc:
        assert str(exc) == "fill_price must be positive"


def test_missing_order_id_rejected():
    fill = ExecutionFill("AAPL", "BUY", 10, 150.0, "", PositionIntent.OPEN_LONG, datetime.now(UTC))
    try:
        fill.validate()
        assert False
    except ValueError as exc:
        assert str(exc) == "broker_order_id is required"


def test_invalid_intent_rejected():
    fill = ExecutionFill("AAPL", "BUY", 10, 150.0, "ORDER-1", "OPEN_LONG", datetime.now(UTC))
    try:
        fill.validate()
        assert False
    except ValueError as exc:
        assert str(exc) == "intent must be a PositionIntent"


def test_invalid_timestamp_rejected():
    fill = ExecutionFill("AAPL", "BUY", 10, 150.0, "ORDER-1", PositionIntent.OPEN_LONG, "not-a-datetime")
    try:
        fill.validate()
        assert False
    except ValueError as exc:
        assert str(exc) == "timestamp must be a datetime"


def test_open_long_and_close_long():
    from trading.portfolio.accounting import PortfolioAccounting
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    a=PortfolioAccounting()
    r=a.apply_fill(ExecutionFill("AAPL", "BUY", 10, 150.0, "L1", PositionIntent.OPEN_LONG, ts))
    assert r.realized_pnl == 0.0
    r=a.apply_fill(ExecutionFill("AAPL", "SELL", 4, 160.0, "L2", PositionIntent.CLOSE_LONG, ts))
    assert r.realized_pnl == 40.0
    assert r.closed_quantity == 4
    assert a.ledger.get_inventory("AAPL", "LONG") == 6


def test_open_short_and_close_short():
    from trading.portfolio.accounting import PortfolioAccounting
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    a=PortfolioAccounting()
    a.apply_fill(ExecutionFill("AAPL", "SELL", 10, 150.0, "S1", PositionIntent.OPEN_SHORT, ts))
    r=a.apply_fill(ExecutionFill("AAPL", "BUY", 4, 140.0, "S", PositionIntent.CLOSE_SHORT, ts))
    assert r.realized_pnl == 40.0
    assert r.closed_quantity == 4
    assert a.ledger.get_inventory("AAPL", "SHORT") == 6


def test_fifo_preserved_through_accounting():
    from trading.portfolio.accounting import PortfolioAccounting
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    a=PortfolioAccounting()
    a.apply_fill(ExecutionFill("AAPL", "BUY", 2, 100.0, "F1", PositionIntent.OPEN_LONG, ts))
    a.apply_fill(ExecutionFill("AAPL", "BUY", 3, 110.0, "F2", PositionIntent.OPEN_LONG, ts))
    r=a.apply_fill(ExecutionFill("AAPL", "SELL", 4, 120.0, "F3", PositionIntent.CLOSE_LONG, ts))
    assert r.realized_pnl == 60.0
    assert r.closed_quantity == 4
    assert a.ledger.get_inventory("AAPL", "LONG") == 1


def test_long_short_isolation_through_accounting():
    from trading.portfolio.accounting import PortfolioAccounting
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    a=PortfolioAccounting()
    a.apply_fill(ExecutionFill("AAPL", "BUY", 5, 100.0, "L1", PositionIntent.OPEN_LONG, ts))
    a.apply_fill(ExecutionFill("AAPL", "SELL", 3, 100.0, "S1", PositionIntent.OPEN_SHORT, ts))
    a.apply_fill(ExecutionFill("AAPL", "SELL", 2, 110.0, "L2", PositionIntent.CLOSE_LONG, ts))
    assert a.ledger.get_inventory("AAPL", "LONG") == 3
    assert a.ledger.get_inventory("AAPL", "SHORT") == 3


def test_mismatched_intent_and_side_rejected():
    from trading.portfolio.accounting import PortfolioAccounting
    import pytest
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    a=PortfolioAccounting()
    with pytest.raises(ValueError, match="requires SELL side"):
        a.apply_fill(ExecutionFill("AAPL", "BUY", 1, 100.0, "X1", PositionIntent.CLOSE_LONG, ts))
    with pytest.raises(ValueError, match="requires BUY side"):
        a.apply_fill(ExecutionFill("AAPL", "SELL", 1, 100.0, "X2", PositionIntent.CLOSE_SHORT, ts))


def test_insufficient_inventory_rejected():
    from trading.portfolio.accounting import PortfolioAccounting
    import pytest
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    a=PortfolioAccounting()
    a.apply_fill(ExecutionFill("AAPL", "BUY", 2, 100.0, "I1", PositionIntent.OPEN_LONG, ts))
    with pytest.raises(ValueError):
        a.apply_fill(ExecutionFill("AAPL", "SELL", 3, 110.0, "I2", PositionIntent.CLOSE_LONG, ts))
def test_exact_duplicate_fill_rejected_without_inventory_change():
    from trading.portfolio.accounting import PortfolioAccounting
    import pytest
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    a=PortfolioAccounting()
    fill=ExecutionFill("AAPL", "BUY", 2, 100.0, "D1", PositionIntent.OPEN_LONG, ts)
    a.apply_fill(fill)
    with pytest.raises(ValueError, match="duplicate fill rejected"):
        a.apply_fill(fill)
    assert a.ledger.get_inventory("AAPL", "LONG") == 2


def test_same_broker_order_id_with_distinct_fill_is_allowed():
    from trading.portfolio.accounting import PortfolioAccounting
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    a=PortfolioAccounting()
    a.apply_fill(ExecutionFill("AAPL", "BUY", 2, 100.0, "D2", PositionIntent.OPEN_LONG, ts))
    a.apply_fill(ExecutionFill("AAPL", "BUY", 1, 101.0, "D2", PositionIntent.OPEN_LONG, datetime(2026, 1, 1, 0, 1, tzinfo=UTC)))
    assert a.ledger.get_inventory("AAPL", "LONG") == 3


def test_failed_close_is_not_recorded_and_retry_can_succeed():
    from trading.portfolio.accounting import PortfolioAccounting
    import pytest
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    a=PortfolioAccounting()
    a.apply_fill(ExecutionFill("AAPL", "BUY", 2, 100.0, "R1", PositionIntent.OPEN_LONG, ts))
    failed=ExecutionFill("AAPL", "SELL", 3, 110.0, "R2", PositionIntent.CLOSE_LONG, ts)
    with pytest.raises(ValueError):
        a.apply_fill(failed)
    a.apply_fill(ExecutionFill("AAPL", "BUY", 1, 101.0, "R3", PositionIntent.OPEN_LONG, ts))
    r=a.apply_fill(failed)
    assert r.realized_pnl == 29.0
    assert a.ledger.get_inventory("AAPL", "LONG") == 0


def test_fill_from_order_result_maps_filled_order():
    from trading.execution.broker import OrderResult
    from trading.portfolio.accounting import fill_from_order_result
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    result=OrderResult("ORD-1", "FILLED", {"symbol":"AAPL", "side":"BUY", "filled_quantity":2, "fill_price":100.0})
    fill=fill_from_order_result(result, PositionIntent.OPEN_LONG, ts)
    assert fill.symbol == "AAPL"
    assert fill.side == "BUY"
    assert fill.quantity == 2
    assert fill.fill_price == 100.0
    assert fill.broker_order_id == "ORD-1"
    assert fill.intent == PositionIntent.OPEN_LONG
    assert fill.timestamp == ts


def test_fill_from_order_result_uses_quantity_and_price_fallbacks():
    from trading.execution.broker import OrderResult
    from trading.portfolio.accounting import fill_from_order_result
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    result=OrderResult("ORD-2", "FILLED", {"symbol":"BTCUSD", "side":"SELL", "quantity":3, "price":25000.0})
    fill=fill_from_order_result(result, PositionIntent.OPEN_SHORT, ts)
    assert fill.quantity == 3
    assert fill.fill_price == 25000.0


def test_fill_from_order_result_rejects_non_order_result():
    from trading.portfolio.accounting import fill_from_order_result
    import pytest
    with pytest.raises(ValueError, match="order_result must be an OrderResult"):
        fill_from_order_result(object(), PositionIntent.OPEN_LONG, datetime(2026, 1, 1, tzinfo=UTC))


def test_fill_from_order_result_rejects_non_filled_statuses():
    from trading.execution.broker import OrderResult
    from trading.portfolio.accounting import fill_from_order_result
    import pytest
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    for status in ("PENDING", "REJECTED", "CANCELLED"):
        result=OrderResult("ORD-" + status, status, {"symbol":"AAPL", "side":"BUY", "filled_quantity":2, "fill_price":100.0})
        with pytest.raises(ValueError, match="order_result must be FILLED"):
            fill_from_order_result(result, PositionIntent.OPEN_LONG, ts)


def test_fill_from_order_result_accepts_filled_status_case_insensitively():
    from trading.execution.broker import OrderResult
    from trading.portfolio.accounting import fill_from_order_result
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    result=OrderResult("ORD-3", "filled", {"symbol":"AAPL", "side":"BUY", "filled_quantity":1, "fill_price":100.0})
    fill=fill_from_order_result(result, PositionIntent.OPEN_LONG, ts)
    assert fill.quantity == 1


def test_account_filled_order_boundary():
    from trading.execution.broker import OrderResult
    from trading.portfolio.accounting import PortfolioAccounting, account_filled_order
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    a=PortfolioAccounting()
    result=OrderResult("BOUND-1", "FILLED", {"symbol":"AAPL", "side":"BUY", "filled_quantity":2, "fill_price":100.0})
    r=account_filled_order(result, PositionIntent.OPEN_LONG, ts, a)
    assert r.broker_order_id == "BOUND-1"
    assert a.ledger.get_inventory("AAPL", "LONG") == 2


def test_account_filled_order_preserves_explicit_close_intent():
    from trading.execution.broker import OrderResult
    from trading.portfolio.accounting import PortfolioAccounting, account_filled_order
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    a=PortfolioAccounting()
    account_filled_order(OrderResult("BOUND-2A", "FILLED", {"symbol":"AAPL", "side":"BUY", "filled_quantity":2, "fill_price":100.0}), PositionIntent.OPEN_LONG, ts, a)
    r=account_filled_order(OrderResult("BOUND-2B", "FILLED", {"symbol":"AAPL", "side":"SELL", "filled_quantity":1, "fill_price":110.0}), PositionIntent.CLOSE_LONG, ts, a)
    assert r.intent == PositionIntent.CLOSE_LONG
    assert r.realized_pnl == 10.0
    assert a.ledger.get_inventory("AAPL", "LONG") == 1


def test_explicit_fill_id_replay_is_rejected():
    from trading.portfolio.accounting import ExecutionFill, PortfolioAccounting
    import pytest
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    a=PortfolioAccounting()
    fill=ExecutionFill("AAPL", "BUY", 2, 100.0, "ORDER-F", PositionIntent.OPEN_LONG, ts, "FILL-001")
    a.apply_fill(fill)
    with pytest.raises(ValueError, match="duplicate fill rejected"):
        a.apply_fill(ExecutionFill("AAPL", "BUY", 2, 999.0, "ORDER-F", PositionIntent.OPEN_LONG, datetime(2026, 1, 1, 0, 5, tzinfo=UTC), "FILL-001"))
    assert a.ledger.get_inventory("AAPL", "LONG") == 2


def test_distinct_fill_ids_same_order_are_allowed():
    from trading.portfolio.accounting import ExecutionFill, PortfolioAccounting
    ts=datetime(2026, 1, 1, tzinfo=UTC)
    a=PortfolioAccounting()
    a.apply_fill(ExecutionFill("AAPL", "BUY", 2, 100.0, "ORDER-F2", PositionIntent.OPEN_LONG, ts, "FILL-A"))
    a.apply_fill(ExecutionFill("AAPL", "BUY", 3, 101.0, "ORDER-F2", PositionIntent.OPEN_LONG, ts, "FILL-B"))
    assert a.ledger.get_inventory("AAPL", "LONG") == 5
