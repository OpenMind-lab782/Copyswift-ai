from datetime import UTC, datetime
import pytest
from trading.portfolio.ledger import Position, PositionLedger, CloseResult


def test_position_validation():
    now = datetime.now(UTC)
    
    valid = Position("AAPL", "LONG", 100, 150.0, now)
    assert valid.validate() is True
    
    with pytest.raises(ValueError, match="symbol is required"):
        Position("", "LONG", 100, 150.0, now).validate()
    
    with pytest.raises(ValueError, match="side must be LONG or SHORT"):
        Position("AAPL", "BUY", 100, 150.0, now).validate()
    
    with pytest.raises(ValueError, match="quantity must be positive"):
        Position("AAPL", "LONG", 0, 150.0, now).validate()
    
    with pytest.raises(ValueError, match="quantity must be positive"):
        Position("AAPL", "LONG", -10, 150.0, now).validate()
    
    with pytest.raises(ValueError, match="entry_price must be positive"):
        Position("AAPL", "LONG", 100, 0, now).validate()
    
    with pytest.raises(ValueError, match="entry_price must be positive"):
        Position("AAPL", "LONG", 100, -5, now).validate()


def test_position_immutability():
    now = datetime.now(UTC)
    pos = Position("AAPL", "LONG", 100, 150.0, now)
    
    with pytest.raises(Exception):
        pos.quantity = 200


def test_ledger_open_position():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    pos1 = Position("AAPL", "LONG", 100, 150.0, now)
    ledger.open_position(pos1)
    
    positions = ledger.get_positions("AAPL", "LONG")
    assert len(positions) == 1
    assert positions[0].quantity == 100
    assert positions[0].entry_price == 150.0


def test_long_short_isolation():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    long_pos = Position("AAPL", "LONG", 100, 150.0, now, broker_order_id="LONG1")
    short_pos = Position("AAPL", "SHORT", 50, 155.0, now, broker_order_id="SHORT1")
    
    ledger.open_position(long_pos)
    ledger.open_position(short_pos)
    
    long_inventory = ledger.get_inventory("AAPL", "LONG")
    short_inventory = ledger.get_inventory("AAPL", "SHORT")
    
    assert long_inventory == 100
    assert short_inventory == 50
    
    long_positions = ledger.get_positions("AAPL", "LONG")
    short_positions = ledger.get_positions("AAPL", "SHORT")
    
    assert len(long_positions) == 1
    assert len(short_positions) == 1
    assert long_positions[0].broker_order_id == "LONG1"
    assert short_positions[0].broker_order_id == "SHORT1"


def test_close_position_prevents_cross_side_close():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    long_pos = Position("AAPL", "LONG", 100, 150.0, now)
    ledger.open_position(long_pos)
    
    with pytest.raises(ValueError, match="no SHORT positions found"):
        ledger.close_position("AAPL", "SHORT", 50, 160.0)
    
    long_inventory = ledger.get_inventory("AAPL", "LONG")
    assert long_inventory == 100


def test_close_position_insufficient_inventory():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    pos = Position("AAPL", "LONG", 100, 150.0, now)
    ledger.open_position(pos)
    
    with pytest.raises(ValueError, match="insufficient LONG inventory"):
        ledger.close_position("AAPL", "LONG", 150, 160.0)
    
    long_inventory = ledger.get_inventory("AAPL", "LONG")
    assert long_inventory == 100


def test_close_entire_position():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    pos = Position("AAPL", "LONG", 100, 150.0, now)
    ledger.open_position(pos)
    
    result = ledger.close_position("AAPL", "LONG", 100, 160.0)
    
    assert result.closed_quantity == 100
    assert result.realized_pnl == (160.0 - 150.0) * 100
    assert len(result.remaining_positions) == 0
    
    long_inventory = ledger.get_inventory("AAPL", "LONG")
    assert long_inventory == 0


def test_fifo_partial_close():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    pos1 = Position("AAPL", "LONG", 100, 150.0, now, broker_order_id="ORDER1")
    pos2 = Position("AAPL", "LONG", 50, 155.0, now, broker_order_id="ORDER2")
    pos3 = Position("AAPL", "LONG", 75, 152.0, now, broker_order_id="ORDER3")
    
    ledger.open_position(pos1)
    ledger.open_position(pos2)
    ledger.open_position(pos3)
    
    result = ledger.close_position("AAPL", "LONG", 120, 160.0)
    
    expected_pnl = (160.0 - 150.0) * 100 + (160.0 - 155.0) * 20
    assert result.closed_quantity == 120
    assert abs(result.realized_pnl - expected_pnl) < 0.01
    assert len(result.remaining_positions) == 2
    
    remaining_pos = result.remaining_positions[0]
    assert remaining_pos.quantity == 30
    assert remaining_pos.entry_price == 155.0
    assert remaining_pos.broker_order_id == "ORDER2"
    
    all_positions = ledger.get_positions("AAPL", "LONG")
    assert len(all_positions) == 2
    assert all_positions[0].quantity == 30
    assert all_positions[0].broker_order_id == "ORDER2"
    assert all_positions[1].quantity == 75
    assert all_positions[1].broker_order_id == "ORDER3"


def test_fifo_deterministic():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    pos1 = Position("AAPL", "LONG", 100, 150.0, now)
    pos2 = Position("AAPL", "LONG", 100, 155.0, now)
    
    ledger.open_position(pos1)
    ledger.open_position(pos2)
    
    result = ledger.close_position("AAPL", "LONG", 50, 160.0)
    
    expected_pnl = (160.0 - 150.0) * 50
    assert abs(result.realized_pnl - expected_pnl) < 0.01
    
    remaining = ledger.get_positions("AAPL", "LONG")
    assert len(remaining) == 2
    assert remaining[0].quantity == 50
    assert remaining[0].entry_price == 150.0
    assert remaining[1].quantity == 100
    assert remaining[1].entry_price == 155.0


def test_preserve_position_fields_on_partial_close():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    metadata = {"strategy": "momentum", "signal_strength": 0.85}
    pos = Position(
        symbol="AAPL",
        side="LONG",
        quantity=100,
        entry_price=150.0,
        timestamp=now,
        broker_order_id="ORDER123",
        metadata=metadata
    )
    
    ledger.open_position(pos)
    
    result = ledger.close_position("AAPL", "LONG", 40, 160.0)
    
    assert len(result.remaining_positions) == 1
    remaining_pos = result.remaining_positions[0]
    
    assert remaining_pos.quantity == 60
    assert remaining_pos.symbol == "AAPL"
    assert remaining_pos.side == "LONG"
    assert remaining_pos.entry_price == 150.0
    assert remaining_pos.timestamp == now
    assert remaining_pos.broker_order_id == "ORDER123"
    assert remaining_pos.metadata == metadata


def test_realized_pnl_long_profit():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    pos = Position("AAPL", "LONG", 100, 150.0, now)
    ledger.open_position(pos)
    
    result = ledger.close_position("AAPL", "LONG", 100, 160.0)
    
    expected_pnl = (160.0 - 150.0) * 100
    assert abs(result.realized_pnl - expected_pnl) < 0.01
    assert result.realized_pnl > 0


def test_realized_pnl_long_loss():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    pos = Position("AAPL", "LONG", 100, 150.0, now)
    ledger.open_position(pos)
    
    result = ledger.close_position("AAPL", "LONG", 100, 140.0)
    
    expected_pnl = (140.0 - 150.0) * 100
    assert abs(result.realized_pnl - expected_pnl) < 0.01
    assert result.realized_pnl < 0


def test_realized_pnl_short_profit():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    pos = Position("AAPL", "SHORT", 100, 150.0, now)
    ledger.open_position(pos)
    
    result = ledger.close_position("AAPL", "SHORT", 100, 140.0)
    
    expected_pnl = (150.0 - 140.0) * 100
    assert abs(result.realized_pnl - expected_pnl) < 0.01
    assert result.realized_pnl > 0


def test_realized_pnl_short_loss():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    pos = Position("AAPL", "SHORT", 100, 150.0, now)
    ledger.open_position(pos)
    
    result = ledger.close_position("AAPL", "SHORT", 100, 160.0)
    
    expected_pnl = (150.0 - 160.0) * 100
    assert abs(result.realized_pnl - expected_pnl) < 0.01
    assert result.realized_pnl < 0


def test_multiple_symbols():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    aapl_pos = Position("AAPL", "LONG", 100, 150.0, now)
    googl_pos = Position("GOOGL", "LONG", 50, 2800.0, now)
    
    ledger.open_position(aapl_pos)
    ledger.open_position(googl_pos)
    
    assert ledger.get_inventory("AAPL", "LONG") == 100
    assert ledger.get_inventory("GOOGL", "LONG") == 50
    
    result = ledger.close_position("AAPL", "LONG", 50, 160.0)
    assert result.closed_quantity == 50
    
    assert ledger.get_inventory("AAPL", "LONG") == 50
    assert ledger.get_inventory("GOOGL", "LONG") == 50


def test_close_position_validation():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    pos = Position("AAPL", "LONG", 100, 150.0, now)
    ledger.open_position(pos)
    
    with pytest.raises(ValueError, match="symbol is required"):
        ledger.close_position("", "LONG", 50, 160.0)
    
    with pytest.raises(ValueError, match="side must be LONG or SHORT"):
        ledger.close_position("AAPL", "BUY", 50, 160.0)
    
    with pytest.raises(ValueError, match="quantity must be positive"):
        ledger.close_position("AAPL", "LONG", 0, 160.0)
    
    with pytest.raises(ValueError, match="quantity must be positive"):
        ledger.close_position("AAPL", "LONG", -10, 160.0)
    
    with pytest.raises(ValueError, match="exit_price must be positive"):
        ledger.close_position("AAPL", "LONG", 50, 0)
    
    with pytest.raises(ValueError, match="exit_price must be positive"):
        ledger.close_position("AAPL", "LONG", 50, -5)


def test_close_position_no_positions_for_symbol():
    ledger = PositionLedger()
    
    with pytest.raises(ValueError, match="no positions found for symbol AAPL"):
        ledger.close_position("AAPL", "LONG", 50, 160.0)


def test_get_positions_all():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    pos1 = Position("AAPL", "LONG", 100, 150.0, now)
    pos2 = Position("GOOGL", "SHORT", 50, 2800.0, now)
    pos3 = Position("AAPL", "SHORT", 25, 155.0, now)
    
    ledger.open_position(pos1)
    ledger.open_position(pos2)
    ledger.open_position(pos3)
    
    all_positions = ledger.get_positions()
    assert len(all_positions) == 3


def test_get_positions_by_symbol():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    pos1 = Position("AAPL", "LONG", 100, 150.0, now)
    pos2 = Position("GOOGL", "SHORT", 50, 2800.0, now)
    pos3 = Position("AAPL", "SHORT", 25, 155.0, now)
    
    ledger.open_position(pos1)
    ledger.open_position(pos2)
    ledger.open_position(pos3)
    
    aapl_positions = ledger.get_positions("AAPL")
    assert len(aapl_positions) == 2
    
    googl_positions = ledger.get_positions("GOOGL")
    assert len(googl_positions) == 1


def test_get_positions_empty():
    ledger = PositionLedger()
    
    positions = ledger.get_positions()
    assert len(positions) == 0
    
    positions = ledger.get_positions("AAPL")
    assert len(positions) == 0
    
    positions = ledger.get_positions("AAPL", "LONG")
    assert len(positions) == 0


def test_clear():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    pos = Position("AAPL", "LONG", 100, 150.0, now)
    ledger.open_position(pos)
    
    assert len(ledger.get_positions()) == 1
    
    ledger.clear()
    
    assert len(ledger.get_positions()) == 0


def test_has_positions():
    ledger = PositionLedger()
    now = datetime.now(UTC)
    
    assert ledger.has_positions() is False
    assert ledger.has_positions("AAPL") is False
    
    pos = Position("AAPL", "LONG", 100, 150.0, now)
    ledger.open_position(pos)
    
    assert ledger.has_positions() is True
    assert ledger.has_positions("AAPL") is True
    assert ledger.has_positions("GOOGL") is False


print("POSITION_LEDGER_TESTS: PASS")
