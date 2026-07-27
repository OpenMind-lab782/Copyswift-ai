from pathlib import Path
import subprocess
import sys
import tempfile
import os

APP_FILE = Path("app.py")


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def _compile_file(filename):
    """
    Compile a Python file and return the result.
    """

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", filename],
        capture_output=True,
        text=True
    )

    return {
        "success": result.returncode == 0,
        "stderr": result.stderr,
        "stdout": result.stdout
    }


def validate_app():
    """
    Validate the current app.py.
    """

    if not APP_FILE.exists():
        raise FileNotFoundError("app.py not found.")

    return _compile_file(str(APP_FILE))


def validate_text(app_text):
    """
    Validate Python source code stored in memory.

    The code is written to a temporary file,
    compiled, and then the temporary file is removed.
    """

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8"
    ) as tmp:

        tmp.write(app_text)
        temp_name = tmp.name

    try:
        return _compile_file(temp_name)

    finally:

        try:
            os.remove(temp_name)
        except OSError:
            pass


if __name__ == "__main__":

    print("=" * 60)
    print("CopySwift AI Validator")
    print("=" * 60)

    result = validate_app()

    if result["success"]:
        print()
        print("✓ Validation PASSED")
        print("app.py compiled successfully.")
    else:
        print()
        print("✗ Validation FAILED")
        print(result["stderr"])
