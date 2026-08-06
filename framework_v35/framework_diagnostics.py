"""
============================================================
CopySwift AI Framework Diagnostics
============================================================
"""

import sys
from pathlib import Path
from framework_info import get_framework_info

MODULES = [
    "patch_utils",
    "patch_executor",
    "patch_loader",
    "patch_registry",
    "validator",
    "upgrade",
]

ROOT = Path(__file__).resolve().parent


def check_modules():
    results = []

    sys.path.insert(0, str(ROOT))

    for module in MODULES:
        try:
            __import__(module)
            results.append((module, True))
        except Exception as e:
            results.append((module, False, str(e)))

    return results


def check_app():
    return Path("app.py").exists()


def check_backups():
    return Path("backups").exists()


def main():

    info = get_framework_info()

    print("=" * 60)
    print(info["name"])
    print("=" * 60)
    print(f"Framework Version : {info['version']}")
    print(f"Release           : {info['release']}")
    print(f"Status            : {info['status']}")
    print()

    print("Checking Modules...")
    passed = 0

    for result in check_modules():

        if result[1]:
            print(f"[PASS] {result[0]}")
            passed += 1
        else:
            print(f"[FAIL] {result[0]} : {result[2]}")

    print()

    print(f"Modules Passed : {passed}/{len(MODULES)}")

    print()

    print(f"app.py Present : {'YES' if check_app() else 'NO'}")
    print(f"Backup Folder  : {'YES' if check_backups() else 'NO'}")

    print()

    if (
        passed == len(MODULES)
        and check_app()
        and check_backups()
    ):
        print("FRAMEWORK STATUS : HEALTHY")
    else:
        print("FRAMEWORK STATUS : ATTENTION REQUIRED")

    print("=" * 60)


if __name__ == "__main__":
    main()
