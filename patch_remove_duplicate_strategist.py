from pathlib import Path

path = Path("app.py")
lines = path.read_text().splitlines()

start = None
end = None

for i, line in enumerate(lines):
    if line.strip() == "strategist = {" and i > 2885:
        start = i
        continue
    if start is not None and line.strip() == "}":
        end = i
        break

if start is None or end is None:
    raise SystemExit("Duplicate strategist block not found.")

del lines[start:end+1]

path.write_text("\n".join(lines) + "\n")

print("✓ Duplicate strategist block removed.")
