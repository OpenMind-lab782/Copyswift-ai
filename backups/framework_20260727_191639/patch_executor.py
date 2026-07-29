from pathlib import Path
from validator import validate_text

APP_FILE = Path("app.py")


class PatchExecutionError(Exception):
    """Raised when a patch cannot be applied."""
    pass


def load_app():
    if not APP_FILE.exists():
        raise FileNotFoundError("app.py not found.")
    return APP_FILE.read_text(encoding="utf-8")


def save_app(text):
    APP_FILE.write_text(text, encoding="utf-8")


def execute_patch(module):
    """
    Execute a patch safely.

    The patch module must expose:

        apply(app_text)

    and return:

        (updated_text, changes)
    """

    if not hasattr(module, "apply"):
        raise PatchExecutionError(
            f"Patch {module.__name__} has no apply() function."
        )

    original = load_app()

    result = module.apply(original)

    if not isinstance(result, tuple) or len(result) != 2:
        raise PatchExecutionError(
            "Patch apply() must return (updated_text, changes)."
        )

    updated_text, changes = result

    if not isinstance(updated_text, str):
        raise PatchExecutionError(
            "Updated application must be a string."
        )

    validation = validate_text(updated_text)

    if not validation["success"]:
        raise PatchExecutionError(
            validation["stderr"]
        )

    save_app(updated_text)

    if changes is None:
        changes = []

    return {
        "success": True,
        "changes": changes,
        "bytes_before": len(original),
        "bytes_after": len(updated_text)
    }


if __name__ == "__main__":

    print("=" * 60)
    print("CopySwift AI Patch Executor")
    print("=" * 60)
    print()
    print("Module installed successfully.")
    print("Validation-before-save is enabled.")
