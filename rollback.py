from pathlib import Path
import shutil

BACKUP_DIR = Path("backups")
APP_FILE = Path("app.py")


class RollbackError(Exception):
    """Raised when a rollback cannot be completed."""
    pass


def get_latest_backup():
    """
    Return the newest backup file in the backups directory.
    """

    if not BACKUP_DIR.exists():
        raise RollbackError("Backups directory does not exist.")

    backups = sorted(
        BACKUP_DIR.glob("app_*.py"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    if not backups:
        raise RollbackError("No backup files found.")

    return backups[0]


def rollback():
    """
    Restore the latest backup to app.py.
    """

    latest = get_latest_backup()

    shutil.copy2(latest, APP_FILE)

    return {
        "success": True,
        "restored_from": str(latest),
        "bytes_restored": latest.stat().st_size
    }


if __name__ == "__main__":

    print("=" * 60)
    print("CopySwift AI Rollback Manager")
    print("=" * 60)

    try:
        result = rollback()

        print()
        print("✓ Rollback completed successfully.")
        print(f"Backup restored: {result['restored_from']}")
        print(f"Bytes restored: {result['bytes_restored']}")

    except Exception as e:
        print()
        print("✗ Rollback failed.")
        print(e)
