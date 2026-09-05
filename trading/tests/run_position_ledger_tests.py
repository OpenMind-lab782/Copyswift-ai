#!/usr/bin/env python3
import subprocess
import sys


def main():
    print("Running PositionLedger tests...")
    print("=" * 60)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "trading/tests/test_position_ledger.py", "-v"],
        cwd="."
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
