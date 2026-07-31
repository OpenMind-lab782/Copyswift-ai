from pathlib import Path
from datetime import datetime
import shutil
import re
import sys

APP = Path("app.py")

if not APP.exists():
    sys.exit("ERROR: app.py not found")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup = backup_dir / f"app_import_normalized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(APP, backup)

lines = APP.read_text().splitlines()

#
# Collect every top-level import in the file.
#
imports = []
seen = set()
remove_indexes = set()

for i, line in enumerate(lines):
    stripped = line.strip()

    if line.startswith("import ") or line.startswith("from "):
        if stripped not in seen:
            imports.append(stripped)
            seen.add(stripped)

        remove_indexes.add(i)

#
# Preserve shebang / encoding / module docstring if present.
#
header = []

idx = 0

while idx < len(lines):

    line = lines[idx]

    if idx == 0 and line.startswith("#!"):
        header.append(line)
        idx += 1
        continue

    if line.startswith("# -*-"):
        header.append(line)
        idx += 1
        continue

    break

#
# Build remaining source.
#
body = []

for i, line in enumerate(lines):
    if i in remove_indexes:
        continue
    body.append(line)

#
# Remove leading blank lines from body.
#
while body and body[0] == "":
    body.pop(0)

#
# Rebuild file.
#
new_lines = []

new_lines.extend(header)

if header:
    new_lines.append("")

new_lines.extend(imports)

new_lines.append("")

new_lines.extend(body)

APP.write_text("\n".join(new_lines) + "\n")

print("=" * 70)
print("IMPORT NORMALIZATION COMPLETE")
print("=" * 70)
print("Backup :", backup)
print()

print("First 20 imports:\n")

count = 0
for line in new_lines:
    if line.startswith("import ") or line.startswith("from "):
        print(line)
        count += 1
        if count == 20:
            break

print()
print("=" * 70)
print("DONE")
print("=" * 70)
