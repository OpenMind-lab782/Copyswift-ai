from pathlib import Path

path = Path("app.py")
text = path.read_text()

old = """        f"Each variation must be under 60 words, include a hook, the pitch, and a clear call-to-action. "
        f"Separate the 3 variations with '---'. Write in plain text only — no Markdown, no **, no ## headers, no bullet symbols."
"""

new = """        f"Each variation must be under 60 words, include a hook, the pitch, and a clear call-to-action. "
        f"Separate the 3 variations with '---'. "
        f"After the three variations, write a line containing exactly ###STRATEGY###, then provide:\\n"
        f"Objective:\\n"
        f"Best Platform:\\n"
        f"Best Posting Time:\\n"
        f"Marketing Tip:\\n"
        f"Follow-up Campaign:\\n"
        f"A/B Test:\\n"
        f"Write in plain text only. Do not use Markdown."
"""

if old not in text:
    raise SystemExit("Prompt block not found.")

path.write_text(text.replace(old, new))

print("✓ AI prompt upgraded.")
