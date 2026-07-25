"""
CopySwift AI Upgrade Logger
Version: 3.0.0
"""

from pathlib import Path
from datetime import datetime

LOG_FILE = Path(__file__).resolve().parent / "logs" / "upgrade.log"


class UpgradeLogger:

    def __init__(self):
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    def show_log(self):
        if not LOG_FILE.exists():
            print("No log file found.")
            return

        with open(LOG_FILE, "r") as f:
            print(f.read())


if __name__ == "__main__":

    logger = UpgradeLogger()

    logger.log("Upgrade Framework initialized.")

    print("=" * 50)
    print("Upgrade Logger")
    print("=" * 50)

    logger.show_log()
