"""
CopySwift AI Upgrade Manager
Version: 3.0.0
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "version.json"


class UpgradeManager:
    def __init__(self):
        self.root = ROOT
        self.version_file = VERSION_FILE

    def get_version(self):
        if not self.version_file.exists():
            return {}

        with open(self.version_file, "r") as f:
            return json.load(f)

    def save_version(self, data):
        with open(self.version_file, "w") as f:
            json.dump(data, f, indent=4)

    def current_version(self):
        return self.get_version().get("version", "Unknown")

    def current_build(self):
        return self.get_version().get("build", 0)

    def show_status(self):
        info = self.get_version()

        print("=" * 50)
        print("CopySwift AI Upgrade Manager")
        print("=" * 50)
        print("Version :", info.get("version"))
        print("Build   :", info.get("build"))
        print("Status  :", info.get("status"))
        print("Patch   :", info.get("last_patch"))
        print("=" * 50)


if __name__ == "__main__":
    manager = UpgradeManager()
    manager.show_status()
