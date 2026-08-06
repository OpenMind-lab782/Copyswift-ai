from pathlib import Path
from datetime import datetime
import importlib.util
import shutil

from patch_loader import load_patches
from patch_registry import (
    load_registry,
    save_registry,
    register_patch
)
from patch_executor import execute_patch
from rollback import rollback
from logger import log_event


APP_FILE = Path("app.py")
BACKUP_DIR = Path("backups")


def create_backup():
    """
    Create a timestamped backup of app.py.
    """

    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup = BACKUP_DIR / f"app_{timestamp}.py"

    shutil.copy2(APP_FILE, backup)

    return backup


def import_patch(path):
    """
    Dynamically import a patch module.
    """

    spec = importlib.util.spec_from_file_location(
        path.stem,
        path
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


def main():

    print("=" * 60)
    print("CopySwift AI Upgrade Manager v3.0")
    print("=" * 60)

    backup = create_backup()

    print(f"Backup created: {backup}")

    registry = load_registry()

    patches = load_patches()

    applied = 0

    for patch in patches:

        patch_id = patch["id"]

        if patch_id in registry.get("installed_patches", []):

            print(f"Skipping {patch_id}")

            continue

        print(f"Applying {patch_id}")

        try:

            module = patch["module"]

            execute_patch(module)

            register_patch(patch_id)

            log_event(
                patch_id=patch_id,
                status="SUCCESS",
                validation="PASS",
                rollback="NO",
                message="Patch installed successfully."
            )

            applied += 1

            print(f"✓ {patch_id} installed.")

        except Exception as e:

            rollback()

            log_event(
                patch_id=patch_id,
                status="FAILED",
                validation="FAIL",
                rollback="YES",
                message=str(e)
            )

            print()

            print("Upgrade failed.")

            print(e)

            return

    save_registry(registry)

    print()

    print("=" * 60)

    print(f"Upgrade Complete")

    print(f"Patches Installed : {applied}")

    print("=" * 60)


if __name__ == "__main__":
    main()
