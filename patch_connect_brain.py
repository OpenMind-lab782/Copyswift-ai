from pathlib import Path

path = Path("app.py")
text = path.read_text()

imports = """
from brain.memory import load_business_memory
from brain.prompt_builder import build_prompt
from brain.scoring import score_campaign
"""

if "from brain.memory import load_business_memory" not in text:
    marker = "from dotenv import load_dotenv"

    if marker not in text:
        raise SystemExit("Import marker not found.")

    text = text.replace(marker, marker + "\n" + imports)

    path.write_text(text)
    print("✓ Brain imports added.")
else:
    print("Brain imports already present.")
