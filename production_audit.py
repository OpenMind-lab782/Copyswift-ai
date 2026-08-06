import subprocess
import sys

TEST_GROUPS = [
    ("Health API", "tests.test_health_api"),
    ("Ready API", "tests.test_ready_api"),
    ("Diagnostics API", "tests.test_diagnostics_api"),
    ("Settlement Service", "tests.test_settlement_service"),
    ("Settlement Repository", "tests.test_settlement_repository"),
    ("SQLite Settlement Repository", "tests.test_sqlite_settlement_repository"),
    ("Reconciliation Service", "tests.test_reconciliation_service"),
    ("Reconciliation Repository", "tests.test_reconciliation_repository"),
    ("SQLite Reconciliation Repository", "tests.test_sqlite_reconciliation_repository"),
    ("Reconciliation Report Service", "tests.test_reconciliation_report_service"),
    ("Payment Event Service", "tests.test_payment_event_service"),
    ("Payment Event API", "tests.test_payment_event_api"),
]

failed = []

print("=" * 70)
print("Swift Payment Engine Production Audit")
print("=" * 70)

for title, module in TEST_GROUPS:
    print(f"\n>>> {title}")
    result = subprocess.run(
        [sys.executable, "-m", "unittest", module, "-v"]
    )

    if result.returncode != 0:
        failed.append(title)

print("\n" + "=" * 70)

if failed:
    print("AUDIT FAILED")
    print("Failed components:")
    for item in failed:
        print("-", item)
    sys.exit(1)

print("AUDIT PASSED")
print("All production-critical components are operational.")
