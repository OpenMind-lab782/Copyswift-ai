"""
============================================================
CopySwift AI Framework v3.5
Patch Utilities
============================================================
"""

from pathlib import Path
import re


class PatchUtilsError(Exception):
    """Raised when a patch utility fails."""
    pass


def read_file(path):
    path = Path(path)
    return path.read_text(encoding="utf-8")


def write_file(path, text):
    path = Path(path)
    path.write_text(text, encoding="utf-8")


def detect_indent(line):
    """
    Return leading whitespace.
    """
    return re.match(r"^\s*", line).group(0)


def ensure_import(text, import_line):
    """
    Add an import if it does not already exist.
    """
    if import_line in text:
        return text, False

    lines = text.splitlines()

    insert_at = 0

    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1

    lines.insert(insert_at, import_line)

    return "\n".join(lines), True


def replace_once(text, old, new):
    """
    Replace first occurrence.
    """
    if old not in text:
        raise PatchUtilsError(f"Target not found: {old}")

    return text.replace(old, new, 1)


def insert_after(text, anchor, block):
    """
    Insert a block after the first occurrence of an anchor,
    preserving indentation.
    """
    if anchor not in text:
        raise PatchUtilsError(f"Anchor not found: {anchor}")

    lines = text.splitlines()

    for i, line in enumerate(lines):
        if anchor in line:

            indent = detect_indent(line)

            if block in text:
                return text, False

            formatted = "\n".join(
                indent + x if x.strip() else ""
                for x in block.strip("\n").splitlines()
            )

            lines.insert(i + 1, formatted)

            return "\n".join(lines), True

    raise PatchUtilsError(f"Anchor not found: {anchor}")


def insert_before(text, anchor, block):
    """
    Insert a block before the first occurrence of an anchor.
    """

    if anchor not in text:
        raise PatchUtilsError(f"Anchor not found: {anchor}")

    lines = text.splitlines()

    for i, line in enumerate(lines):

        if anchor in line:

            indent = detect_indent(line)

            if block in text:
                return text, False

            formatted = "\n".join(
                indent + x if x.strip() else ""
                for x in block.strip("\n").splitlines()
            )

            lines.insert(i, formatted)

            return "\n".join(lines), True

    raise PatchUtilsError(f"Anchor not found: {anchor}")


def ensure_block(text, block):
    """
    Ensure a block exists.
    """
    if block.strip() in text:
        return text, False

    return text + "\n\n" + block.rstrip() + "\n", True


def replace_all(text, old, new):
    """
    Replace every occurrence.
    """
    if old not in text:
        raise PatchUtilsError(f"Target not found: {old}")

    return text.replace(old, new)


def insert_after_line(text, anchor, block):
    """
    Insert a block after a line containing 'anchor', preserving the
    indentation of the following logical block.
    Returns (updated_text, changed).
    """
    lines = text.splitlines()

    for i, line in enumerate(lines):
        if anchor in line:

            if block.strip() in text:
                return text, False

            # Determine indentation from the next non-empty line.
            indent = ""
            for j in range(i + 1, len(lines)):
                if lines[j].strip():
                    indent = detect_indent(lines[j])
                    break

            formatted = []
            for b in block.strip("\n").splitlines():
                if b.strip():
                    formatted.append(indent + b)
                else:
                    formatted.append("")

            lines.insert(i + 1, "\n".join(formatted))
            return "\n".join(lines), True

    raise PatchUtilsError(f"Anchor not found: {anchor}")

