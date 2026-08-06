from pathlib import Path
import importlib.util

PATCH_DIR = Path("patches")

def load_patches():
    patches = []

    if not PATCH_DIR.exists():
        return patches

    for file in sorted(PATCH_DIR.glob("patch_*.py")):

        spec = importlib.util.spec_from_file_location(
            file.stem,
            file
        )

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        patches.append({
            "id": getattr(module, "PATCH_ID", "Unknown"),
            "description": getattr(module, "DESCRIPTION", ""),
            "module": module,
            "filename": file.name,
        })

    return patches


if __name__ == "__main__":

    print("=" * 60)
    print("CopySwift AI Patch Loader")
    print("=" * 60)

    patches = load_patches()

    if not patches:
        print("No patches found.")
    else:

        for p in patches:

            print()

            print("Patch ID :", p["id"])
            print("File     :", p["filename"])
            print("Summary  :", p["description"])

    print()
    print(f"Total patches discovered: {len(patches)}")
