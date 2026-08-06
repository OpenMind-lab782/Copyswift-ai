from pathlib import Path
from datetime import datetime
import shutil

APP = Path("app.py")

text = APP.read_text()

IMPORT = "from payment_engine.api.merchants import merchant_api"

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup = backup_dir / f"app_import_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(APP, backup)

lines = text.splitlines()

# Remove every existing merchant_api import
lines = [l for l in lines if l.strip() != IMPORT]

# Find the last import statement
last_import = -1
for i, line in enumerate(lines):
    s = line.strip()
    if s.startswith("import ") or s.startswith("from "):
        last_import = i

if last_import >= 0:
    lines.insert(last_import + 1, IMPORT)
else:
    lines.insert(0, IMPORT)

APP.write_text("\n".join(lines) + "\n")

print("=" * 60)
print("Merchant Import Order Fix")
print("=" * 60)
print("Backup :", backup)
print("Status : SUCCESS")
print("=" * 60)
