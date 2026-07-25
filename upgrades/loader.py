"""
CopySwift AI Patch Loader
Version: 3.0.0
"""

from pathlib import Path

PATCH_DIR = Path(__file__).resolve().parent / "patches"


class PatchLoader:
    def __init__(self):
        self.patch_dir = PATCH_DIR

    def discover(self):
        if not self.patch_dir.exists():
            return []

        patches = []

        for patch in self.patch_dir.glob("*.py"):
            if patch.name == "__init__.py":
                continue

            patches.append(patch.name)

        return sorted(patches)


if __name__ == "__main__":
    loader = PatchLoader()

    print("=" * 50)
    print("Available Patches")
    print("=" * 50)

    patches = loader.discover()

    if not patches:
        print("No patches found.")
    else:
        for patch in patches:
            print("•", patch)
