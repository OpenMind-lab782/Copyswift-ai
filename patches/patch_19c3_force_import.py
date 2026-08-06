from pathlib import Path
from datetime import datetime
import shutil
import sys

APP = Path("app.py")

if not APP.exists():
    sys.exit("ERROR: app.py not found")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup = backup_dir / f"app_force_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(APP, backup)

IMPORT = "from payment_engine.api.merchants import merchant_api"

lines = APP.read_text().splitlines()

# Remove every existing merchant_api import
lines = [l for l in lines if l.strip() != IMPORT]

# Find the Flask import
insert_at = None
for i, line in enumerate(lines):
    if line.startswith("from flask import"):
        insert_at = i + 1
        break

if insert_at is None:
    insert_at = 0

lines.insert(insert_at, IMPORT)

APP.write_text("\n".join(lines) + "\n")

print("=" * 60)
print("PATCH COMPLETE")
print("Backup:", backup)
print("=" * 60)

print("\nRelevant lines:\n")

for n, line in enumerate(APP.read_text().splitlines(), 1):
    if (
        line.startswith("from flask import")
        or "merchant_api" in line
        or "register_blueprint" in line
        or "Flask(" in line
    ):
        print(f"{n:4}: {line}")
