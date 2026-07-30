from pathlib import Path

path = Path("app.py")
lines = path.read_text().splitlines()

start = None
end = None

for i, line in enumerate(lines):
    if line.strip() == 'brand_context = ""':
        start = i
    if start is not None and line.strip() == 'prompt = build_prompt(':
        end = i
        break

if start is None or end is None:
    raise SystemExit("Unused brand_context block not found.")

new_lines = lines[:start] + lines[end:]

path.write_text("\n".join(new_lines) + "\n")

print("✓ Removed unused brand_context block.")
