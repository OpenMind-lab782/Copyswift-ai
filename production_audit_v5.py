import subprocess
import sys

TEST_GROUPS = [
    ("Configuration Validator", "tests.test_configuration_validator"),
    ("Health API", "tests.test_health_api"),
    ("Ready API", "tests.test_ready_api"),
    ("Diagnostics API", "tests.test_diagnostics_api"),
    ("Webhook Signature", "tests.test_webhook_signature_verifier"),
    ("Idempotency", "tests.test_idempotency_store"),
    ("Gateway Registry", "tests.test_gateway_registry"),
    ("Gateway Metrics", "tests.test_gateway_metrics"),
    ("Merchant Routing Policy", "tests.test_merchant_routing_policy"),
    ("Capability-Aware Routing", "tests.test_capability_aware_routing"),
    ("Payment Flow Integration", "tests.test_payment_flow_integration"),
]

failed = []

print("=" * 72)
print("Swift Payment Engine v5.0.0 Production Audit")
print("=" * 72)

for title, module in TEST_GROUPS:
    print(f"\n>>> {title}")

    result = subprocess.run(
        [sys.executable, "-m", "unittest", module, "-v"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    print(result.stdout)

    if result.returncode != 0:
        failed.append((title, result.returncode))

print("=" * 72)

if failed:
    print("AUDIT FAILED")
    print()

    for title, code in failed:
        print(f"- {title} (return code={code})")

    sys.exit(1)

print("AUDIT PASSED")
print("Swift Payment Engine v5.0.0 is production certified.")
