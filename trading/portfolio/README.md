# PositionLedger - Production-Safe Paper Trading Accounting

## Overview

The `PositionLedger` provides a production-safe foundation for paper-trading position accounting with proper isolation of long and short positions, FIFO inventory management, and accurate P&L calculation.

## Key Features

1. **Long/Short Isolation**: Long and short positions for the same symbol are tracked separately and never mixed
2. **Explicit Side Identification**: `close_position()` requires explicit side to prevent accidental cross-side closes
3. **FIFO Partial Closes**: Deterministic first-in-first-out behavior when closing positions
4. **Field Preservation**: All Position metadata preserved during partial closes
5. **Inventory Validation**: Prevents closing more inventory than exists
6. **Correct P&L Calculation**: Proper realized P&L for both long and short positions

## Usage Examples

### Opening Positions

```python
from datetime import datetime, UTC
from trading.portfolio.ledger import Position, PositionLedger

ledger = PositionLedger()

# Open a long position
long_pos = Position(
    symbol="AAPL",
    side="LONG",
    quantity=100,
    entry_price=150.0,
    timestamp=datetime.now(UTC),
    broker_order_id="ORDER-123",
    metadata={"strategy": "momentum"}
)
ledger.open_position(long_pos)

# Open a short position (isolated from long)
short_pos = Position(
    symbol="AAPL",
    side="SHORT",
    quantity=50,
    entry_price=155.0,
    timestamp=datetime.now(UTC),
    broker_order_id="ORDER-124"
)
ledger.open_position(short_pos)
```

### Closing Positions (FIFO)

```python
# Close 60 shares of LONG position
result = ledger.close_position(
    symbol="AAPL",
    side="LONG",
    quantity=60,
    exit_price=160.0
)

print(f"Realized P&L: ${result.realized_pnl:.2f}")
print(f"Closed quantity: {result.closed_quantity}")
print(f"Remaining positions: {len(result.remaining_positions)}")
```

### Querying Positions

```python
# Get all positions
all_positions = ledger.get_positions()

# Get positions for a specific symbol
aapl_positions = ledger.get_positions("AAPL")

# Get positions for a specific symbol and side
long_positions = ledger.get_positions("AAPL", "LONG")

# Get inventory quantity
long_inventory = ledger.get_inventory("AAPL", "LONG")
short_inventory = ledger.get_inventory("AAPL", "SHORT")
```

## P&L Calculations

### Long Positions
- **Profit**: Exit price > Entry price
- **Formula**: `(exit_price - entry_price) * quantity`
- **Example**: Buy at $150, sell at $160, quantity 100 = $(160-150) * 100 = $1,000 profit

### Short Positions
- **Profit**: Exit price < Entry price
- **Formula**: `(entry_price - exit_price) * quantity`
- **Example**: Short at $150, cover at $140, quantity 100 = $(150-140) * 100 = $1,000 profit

## FIFO Behavior

When closing positions, the ledger uses First-In-First-Out (FIFO) ordering:

```python
# Open three positions
ledger.open_position(Position("AAPL", "LONG", 100, 150.0, timestamp1))
ledger.open_position(Position("AAPL", "LONG", 50, 155.0, timestamp2))
ledger.open_position(Position("AAPL", "LONG", 75, 152.0, timestamp3))

# Close 120 shares
result = ledger.close_position("AAPL", "LONG", 120, 160.0)

# FIFO: Closes entire first position (100) + 20 from second position (50)
# Remaining: 30 shares at $155 (from pos 2) + 75 shares at $152 (pos 3)
```

## Safety Features

### Side Isolation

```python
# Open long position
ledger.open_position(Position("AAPL", "LONG", 100, 150.0, now))

# This will FAIL - cannot close SHORT when only LONG exists
ledger.close_position("AAPL", "SHORT", 50, 160.0)  # raises ValueError
```

### Insufficient Inventory Prevention

```python
# Open 100 shares
ledger.open_position(Position("AAPL", "LONG", 100, 150.0, now))

# This will FAIL - cannot close more than available
ledger.close_position("AAPL", "LONG", 150, 160.0)  # raises ValueError
```

## Testing

Run comprehensive unit tests with: `python -m pytest trading/tests/test_position_ledger.py -v`
