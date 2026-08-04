import importlib
import os
import platform
import sqlite3
import sys

print("=" * 72)
print("Swift Payment Engine v5.0.0 Render Deployment Verification")
print("=" * 72)

print("\nPython")
print("-" * 72)
print(platform.python_version())

print("\nApplication Import")
print("-" * 72)

try:
    import app
    print("PASS - app.py imports successfully")
except Exception as e:
    print("FAIL - app.py import failed")
    print(e)
    sys.exit(1)

print("\nDatabase")
print("-" * 72)

try:
    conn = sqlite3.connect(":memory:")
    conn.execute("SELECT 1")
    conn.close()
    print("PASS - SQLite operational")
except Exception as e:
    print("FAIL - SQLite error")
    print(e)
    sys.exit(1)

print("\nEnvironment Variables")
print("-" * 72)

required = [
    "SECRET_KEY",
    "GROQ_API_KEY",
]

missing = []

for key in required:
    if os.environ.get(key):
        print(f"PASS - {key}")
    else:
        print(f"WARN - {key} not set")
        missing.append(key)

print("\nGunicorn")
print("-" * 72)

try:
    importlib.import_module("gunicorn")
    print("PASS - Gunicorn installed")
except Exception:
    print("WARN - Gunicorn not installed in current environment")

print("\n" + "=" * 72)

if missing:
    print("DEPLOYMENT READY WITH WARNINGS")
    print("Missing environment variables:")
    for item in missing:
        print("-", item)
else:
    print("DEPLOYMENT READY")

print("=" * 72)
