"""
CopySwift AI Rollback Manager
Version: 3.0.0
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = ROOT / "upgrades" / "backups"


class RollbackManager:

    def __init__(self):
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    def backup_file(self, file_path):
        src = Path(file_path)

        if not src.exists():
            return False, "Source file not found."

        dest = BACKUP_DIR / (src.name + ".bak")
        shutil.copy2(src, dest)

        return True, str(dest)


if __name__ == "__main__":

    manager = RollbackManager()

    status, result = manager.backup_file(ROOT / "version.json")

    print("=" * 50)
    print("Rollback Manager")
    print("=" * 50)
    print("Status :", status)
    print("Backup :", result)
