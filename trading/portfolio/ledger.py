from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Position:
    symbol: str
    side: str
    quantity: float
    entry_price: float
    timestamp: datetime
    broker_order_id: str = ""
    metadata: dict[str, Any] | None = None

    def validate(self):
        if not self.symbol.strip():
            raise ValueError("symbol is required")
        if self.side.upper() not in {"LONG", "SHORT"}:
            raise ValueError("side must be LONG or SHORT")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.entry_price <= 0:
            raise ValueError("entry_price must be positive")
        return True


@dataclass(frozen=True)
class CloseResult:
    realized_pnl: float
    closed_quantity: float
    remaining_positions: list[Position]


class PositionLedger:
    def __init__(self):
        self._positions: dict[str, dict[str, list[Position]]] = {}

    def open_position(self, position: Position) -> None:
        position.validate()
        
        symbol = position.symbol
        side = position.side.upper()
        
        if symbol not in self._positions:
            self._positions[symbol] = {"LONG": [], "SHORT": []}
        
        self._positions[symbol][side].append(position)

    def close_position(
        self,
        symbol: str,
        side: str,
        quantity: float,
        exit_price: float
    ) -> CloseResult:
        if not symbol.strip():
            raise ValueError("symbol is required")
        
        side = side.upper()
        if side not in {"LONG", "SHORT"}:
            raise ValueError("side must be LONG or SHORT")
        
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        
        if exit_price <= 0:
            raise ValueError("exit_price must be positive")
        
        if symbol not in self._positions:
            raise ValueError(f"no positions found for symbol {symbol}")
        
        positions = self._positions[symbol][side]
        
        if not positions:
            raise ValueError(f"no {side} positions found for symbol {symbol}")
        
        total_inventory = sum(p.quantity for p in positions)
        if quantity > total_inventory:
            raise ValueError(
                f"insufficient {side} inventory for {symbol}: "
                f"requested {quantity}, available {total_inventory}"
            )
        
        remaining_qty = quantity
        realized_pnl = 0.0
        remaining_positions = []
        
        for position in positions:
            if remaining_qty <= 0:
                remaining_positions.append(position)
                continue
            
            if position.quantity <= remaining_qty:
                qty_closed = position.quantity
                remaining_qty -= qty_closed
                
                if side == "LONG":
                    pnl = (exit_price - position.entry_price) * qty_closed
                else:
                    pnl = (position.entry_price - exit_price) * qty_closed
                
                realized_pnl += pnl
            else:
                qty_closed = remaining_qty
                remaining_qty = 0
                
                if side == "LONG":
                    pnl = (exit_price - position.entry_price) * qty_closed
                else:
                    pnl = (position.entry_price - exit_price) * qty_closed
                
                realized_pnl += pnl
                
                new_quantity = position.quantity - qty_closed
                reduced_position = replace(position, quantity=new_quantity)
                remaining_positions.append(reduced_position)
        
        self._positions[symbol][side] = remaining_positions
        
        return CloseResult(
            realized_pnl=realized_pnl,
            closed_quantity=quantity,
            remaining_positions=remaining_positions
        )

    def get_positions(self, symbol: str = None, side: str = None) -> list[Position]:
        if symbol is None:
            result = []
            for sym_positions in self._positions.values():
                for side_positions in sym_positions.values():
                    result.extend(side_positions)
            return result
        
        if symbol not in self._positions:
            return []
        
        if side is None:
            result = []
            for side_positions in self._positions[symbol].values():
                result.extend(side_positions)
            return result
        
        side = side.upper()
        if side not in {"LONG", "SHORT"}:
            raise ValueError("side must be LONG or SHORT")
        
        return list(self._positions[symbol][side])

    def get_inventory(self, symbol: str, side: str) -> float:
        side = side.upper()
        if side not in {"LONG", "SHORT"}:
            raise ValueError("side must be LONG or SHORT")
        
        if symbol not in self._positions:
            return 0.0
        
        positions = self._positions[symbol][side]
        return sum(p.quantity for p in positions)

    def clear(self) -> None:
        self._positions.clear()

    def get_all_symbols(self) -> set[str]:
        return set(self._positions.keys())

    def has_positions(self, symbol: str = None) -> bool:
        if symbol is None:
            return len(self._positions) > 0
        
        if symbol not in self._positions:
            return False
        
        long_qty = sum(p.quantity for p in self._positions[symbol]["LONG"])
        short_qty = sum(p.quantity for p in self._positions[symbol]["SHORT"])
        return long_qty > 0 or short_qty > 0
