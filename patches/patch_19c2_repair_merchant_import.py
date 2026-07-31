from pathlib import Path
from datetime import datetime
import shutil

APP = Path("app.py")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup = backup_dir / f"app_repair_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(APP, backup)

IMPORT = "from payment_engine.api.merchants import merchant_api"

text = APP.read_text()

# Add the import immediately after the Flask import if it doesn't already exist.
if IMPORT not in text:
    marker = "from flask import"
    lines = text.splitlines()

    inserted = False
    for i, line in enumerate(lines):
        if line.startswith(marker):
            lines.insert(i + 1, IMPORT)
            inserted = True
            break

    if not inserted:
        lines.insert(0, IMPORT)

    text = "\n".join(lines) + "\n"
    APP.write_text(text)

print("=" * 60)
print("Merchant Import Repair")
print("=" * 60)
print("Backup :", backup)
print("Status : SUCCESS")
print("=" * 60)
