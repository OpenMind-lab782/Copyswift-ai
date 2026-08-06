from pathlib import Path
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "framework_v35"))

from patch_utils import ensure_import

print("=" * 60)
print("Framework v3.5 E2E Patch Execution")
print("=" * 60)

sample = """from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "OK"
"""

with tempfile.TemporaryDirectory() as tmp:

    app_file = Path(tmp) / "app.py"
    app_file.write_text(sample, encoding="utf-8")

    text = app_file.read_text(encoding="utf-8")

    updated, changed = ensure_import(
        text,
        "import os"
    )

    app_file.write_text(updated, encoding="utf-8")

    final = app_file.read_text(encoding="utf-8")

    if "import os" not in final:
        raise RuntimeError("Patch failed.")

    print("[PASS] ensure_import()")
    print("[PASS] Patch applied")
    print("[PASS] Verification successful")

print("-" * 60)
print("STATUS: PASS")
print("=" * 60)
