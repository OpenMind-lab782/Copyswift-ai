from pathlib import Path
from datetime import datetime
import shutil

APP = Path("app.py")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup = backup_dir / f"app_fix_import_order_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(APP, backup)

lines = APP.read_text().splitlines()

TARGETS = [
    "from payment_engine.engine import PaymentEngine",
    "from payment_engine.models import PaymentRequest",
]

found = []

new_lines = []

for line in lines:
    if line.strip() in TARGETS:
        found.append(line.strip())
    else:
        new_lines.append(line)

insert_at = 0

for i, line in enumerate(new_lines):
    if line.startswith("import ") or line.startswith("from "):
        insert_at = i + 1

for item in reversed(found):
    new_lines.insert(insert_at, item)

APP.write_text("\n".join(new_lines) + "\n")

print("=" * 60)
print("PaymentEngine Import Order Fixed")
print("=" * 60)
print("Backup:", backup)
print()

for i, line in enumerate(new_lines[:120], 1):
    if "PaymentEngine" in line or "PaymentRequest" in line:
        print(f"{i:4}: {line}")

print("=" * 60)
