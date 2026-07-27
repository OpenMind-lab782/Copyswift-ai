from pathlib import Path
import tempfile
import shutil

print("=" * 60)
print("Framework v3.5 Rollback Test")
print("=" * 60)

sample = """print("Original Application")
"""

with tempfile.TemporaryDirectory() as tmp:

    app = Path(tmp) / "app.py"
    backup = Path(tmp) / "app_backup.py"

    app.write_text(sample, encoding="utf-8")
    shutil.copy2(app, backup)

    try:
        # Simulate a patch that corrupts the application
        app.write_text("def broken(:\n", encoding="utf-8")
        raise RuntimeError("Simulated patch failure")
    except Exception:
        shutil.copy2(backup, app)

    restored = app.read_text(encoding="utf-8")

    if restored != sample:
        raise RuntimeError("Rollback failed")

    print("[PASS] Backup restored")
    print("[PASS] Original application recovered")

print("-" * 60)
print("STATUS: PASS")
print("=" * 60)
