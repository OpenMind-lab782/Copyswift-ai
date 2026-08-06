from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import sys

UPGRADE_FILE = Path("upgrade.py")
BACKUP_DIR = Path("backups")


def backup():
    BACKUP_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = BACKUP_DIR / f"upgrade_{ts}.py"
    shutil.copy2(UPGRADE_FILE, dst)
    return dst


def patch_text(text):
    old = 'module = import_patch(Path(patch["file"]))'
    new = 'module = patch["module"]'

    if old not in text:
        return text, False

    text = text.replace(old, new)

    return text, True


def validate():
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", "upgrade.py"],
        capture_output=True,
        text=True
    )

    return result.returncode == 0, result.stderr


def main():

    print("=" * 60)
    print("CopySwift AI Upgrade Bootstrap")
    print("=" * 60)

    if not UPGRADE_FILE.exists():
        print("upgrade.py not found.")
        return

    backup_file = backup()
    print(f"Backup created: {backup_file}")

    original = UPGRADE_FILE.read_text(encoding="utf-8")

    updated, changed = patch_text(original)

    if not changed:
        print("No bootstrap changes were required.")
        return

    UPGRADE_FILE.write_text(updated, encoding="utf-8")

    ok, err = validate()

    if ok:
        print("✓ Bootstrap repair completed successfully.")
    else:
        print("✗ Validation failed.")
        print(err)
        shutil.copy2(backup_file, UPGRADE_FILE)
        print("Original upgrade.py restored.")


if __name__ == "__main__":
    main()
