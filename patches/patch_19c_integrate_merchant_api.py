from pathlib import Path
from datetime import datetime
import shutil
import re

APP = Path("app.py")

if not APP.exists():
    raise SystemExit("ERROR: app.py not found.")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"app_{timestamp}.py"

shutil.copy2(APP, backup)

text = APP.read_text()

IMPORT_LINE = "from payment_engine.api.merchants import merchant_api"

if IMPORT_LINE not in text:

    imports = list(re.finditer(r"^from .*$|^import .*$", text, re.MULTILINE))

    if imports:
        pos = imports[-1].end()
        text = text[:pos] + "\n" + IMPORT_LINE + text[pos:]
    else:
        text = IMPORT_LINE + "\n\n" + text

REGISTER = 'app.register_blueprint(merchant_api, url_prefix="/api/v1")'

if REGISTER not in text:

    m = re.search(r"app\s*=\s*Flask\s*\([^\n]*\)", text)

    if not m:
        raise SystemExit("ERROR: Could not locate Flask app creation.")

    insert = "\n\n" + REGISTER + "\n"

    text = text[:m.end()] + insert + text[m.end():]

APP.write_text(text)

print("=" * 60)
print(" Merchant API Integration Patch")
print("=" * 60)
print("Backup :", backup)
print("Import : OK")
print("Register : OK")
print("Status : SUCCESS")
print("=" * 60)

