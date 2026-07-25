"""
CopySwift AI Patch Registry
Version: 3.0.0
"""

import json
from pathlib import Path

REGISTRY_FILE = Path(__file__).resolve().parent / "patch_registry.json"


class PatchRegistry:

    def __init__(self):
        self.registry = REGISTRY_FILE

        if not self.registry.exists():
            self.save([])

    def load(self):
        with open(self.registry, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(self.registry, "w") as f:
            json.dump(data, f, indent=4)

    def register(self, patch_name):
        patches = self.load()

        if patch_name not in patches:
            patches.append(patch_name)
            self.save(patches)

    def is_installed(self, patch_name):
        return patch_name in self.load()

    def list_patches(self):
        return self.load()


if __name__ == "__main__":

    registry = PatchRegistry()

    print("=" * 50)
    print("Installed Patches")
    print("=" * 50)

    patches = registry.list_patches()

    if not patches:
        print("No installed patches.")
    else:
        for patch in patches:
            print("•", patch)
