from pathlib import Path

path = Path("app.py")
text = path.read_text()

old = """    prompt = (
        brand_context +
        f"Write 3 short ad copy variations for {platform}, in a {tone} tone.\\n"
        f"What's being sold: {offer}\\n"
        f"Target customer: {customer or 'general African small business customers'}\\n"
        f"Their main hesitation to address: {hesitation or 'none specified'}\\n"
        f"Each variation must be under 60 words, include a hook, the pitch, and a clear call-to-action. "
        f"Separate the 3 variations with '---'. "
        f"After the three variations, write a line containing exactly ###STRATEGY###, then provide:\\n"
        f"Objective:\\n"
        f"Best Platform:\\n"
        f"Best Posting Time:\\n"
        f"Marketing Tip:\\n"
        f"Follow-up Campaign:\\n"
        f"A/B Test:\\n"
        f"Write in plain text only. Do not use Markdown."
    )
"""

new = """    prompt = build_prompt(
        profile,
        offer,
        customer,
        hesitation,
        platform,
        tone,
    )
"""

if old not in text:
    raise SystemExit("Prompt block not found. No changes made.")

path.write_text(text.replace(old, new))

print("✓ REST API now uses Prompt Builder.")
