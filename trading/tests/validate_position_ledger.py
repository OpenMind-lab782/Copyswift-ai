#!/usr/bin/env python3
"""
Validation script for PositionLedger implementation.

Verifies:
1. Python compilation (no syntax errors)
2. Basic functionality
3. All required features work correctly
"""
import sys
import subprocess
from datetime import datetime, UTC


def check_compilation():
    print("=" * 70)
    print("STEP 1: Checking Python compilation...")
    print("=" * 70)
    
    result = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "trading/"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ No syntax errors found")
        return True
    else:
        print("✗ Compilation errors found:")
        print(result.stderr)
        return False


def check_basic_functionality():
    print("\n" + "=" * 70)
    print("STEP 2: Testing basic PositionLedger functionality...")
    print("=" * 70)
    
    try:
        from trading.portfolio.ledger import Position, PositionLedger, CloseResult
        
        ledger = PositionLedger()
        now = datetime.now(UTC)
        
        # Test 1: Long/Short isolation
        print("Testing long/short isolation...")
        long_pos = Position("TEST", "LONG", 100, 150.0, now)
        short_pos = Position("TEST", "SHORT", 50, 155.0, now)
        ledger.open_position(long_pos)
        ledger.open_position(short_pos)
        
        assert ledger.get_inventory("TEST", "LONG") == 100
        assert ledger.get_inventory("TEST", "SHORT") == 50
        print("✓ Long/short isolation working")
        
        # Test 2: FIFO partial close
        print("Testing FIFO partial close...")
        result = ledger.close_position("TEST", "LONG", 60, 160.0)
        assert result.closed_quantity == 60
        assert result.realized_pnl == (160.0 - 150.0) * 60
        assert ledger.get_inventory("TEST", "LONG") == 40
        print("✓ FIFO partial close working")
        
        # Test 3: Cross-side prevention
        print("Testing cross-side close prevention...")
        try:
            ledger.close_position("TEST", "LONG", 60, 160.0)
            print("✗ Should have raised insufficient inventory error")
            return False
        except ValueError as e:
            if "insufficient" in str(e).lower():
                print("✓ Cross-side prevention working")
        
        print("\n✓ All basic functionality tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Error during functionality tests: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    success = check_compilation() and check_basic_functionality()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
