from pathlib import Path
from datetime import datetime

LOG_FILE = Path("upgrade.log")


def log_event(
    patch_id="SYSTEM",
    status="INFO",
    validation="N/A",
    rollback="NO",
    message=""
):
    """
    Write an upgrade event to upgrade.log.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = (
        "=" * 60 + "\n"
        f"Timestamp : {timestamp}\n"
        f"Patch ID  : {patch_id}\n"
        f"Status    : {status}\n"
        f"Validation: {validation}\n"
        f"Rollback  : {rollback}\n"
    )

    if message:
        entry += f"Message   : {message}\n"

    entry += "=" * 60 + "\n\n"

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(entry)


if __name__ == "__main__":

    print("=" * 60)
    print("CopySwift AI Upgrade Logger")
    print("=" * 60)

    log_event(
        patch_id="TEST",
        status="SUCCESS",
        validation="PASS",
        rollback="NO",
        message="Logger module test completed."
    )

    print()
    print("✓ Test log written successfully.")
    print(f"Log file: {LOG_FILE}")
