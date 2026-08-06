import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "framework_v35"))

modules = [
    "patch_utils",
    "patch_executor",
    "patch_loader",
    "patch_registry",
    "validator",
    "upgrade",
]

print("=" * 60)
print("CopySwift AI Framework v3.5 Health Check")
print("=" * 60)

passed = 0

for name in modules:
    try:
        __import__(name)
        print(f"[PASS] {name}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] {name}: {e}")

print("-" * 60)
print(f"Passed: {passed}/{len(modules)}")

if passed == len(modules):
    print("STATUS: HEALTHY")
else:
    print("STATUS: FAILED")
    raise SystemExit(1)
