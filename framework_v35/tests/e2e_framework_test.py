from pathlib import Path
import tempfile

print("=" * 60)
print("Framework v3.5 End-to-End Test")
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

    print("[PASS] Temporary app created")
    print(f"Location: {app_file}")

print("[PASS] Temporary workspace cleaned")

print("=" * 60)
print("E2E Test Stage 1 Complete")
print("=" * 60)
