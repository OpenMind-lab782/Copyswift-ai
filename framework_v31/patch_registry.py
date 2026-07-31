from pathlib import Path
import json

VERSION_FILE = Path("version.json")

def _default():
    return {
        "version": "3.0.0",
        "last_upgrade": "",
        "installed_patches": []
    }

def load_registry():
    if not VERSION_FILE.exists():
        data = _default()
        VERSION_FILE.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )
        return data

    try:
        data = json.loads(
            VERSION_FILE.read_text(encoding="utf-8")
        )
    except Exception:
        data = _default()

    if "installed_patches" not in data:
        data["installed_patches"] = []

    return data

def save_registry(data):
    VERSION_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

def is_installed(patch_id):
    data = load_registry()
    return patch_id in data["installed_patches"]

def register_patch(patch_id):
    data = load_registry()

    if patch_id not in data["installed_patches"]:
        data["installed_patches"].append(patch_id)

    save_registry(data)

if __name__ == "__main__":

    registry = load_registry()

    print("=" * 60)
    print("CopySwift AI Patch Registry")
    print("=" * 60)
    print(json.dumps(registry, indent=2))
