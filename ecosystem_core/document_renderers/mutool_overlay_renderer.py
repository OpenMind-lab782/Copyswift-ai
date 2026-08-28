"""
CopySwiftAI Document Studio - Immutable overlay renderer.

Preserves the original PDF content, style, and background completely
unchanged. Only text that was actually added or edited by the user is
redacted (text-only) and redrawn; everything else in the source PDF
is left byte-for-byte untouched.
"""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path


class MutoolOverlayRenderer:
    """PDF renderer backed by mutool run, using redact+overlay technique."""

    SCRIPT_PATH = Path(__file__).parent.parent / "mutool_scripts" / "apply_overlay.js"

    def __init__(self):
        self.mutool = shutil.which("mutool")

    def render(self, document, output_name="output.pdf"):
        if not isinstance(document, dict):
            raise TypeError("Document must be a dictionary.")

        if not self.mutool:
            raise RuntimeError("mutool binary is not available on PATH.")

        original_bytes = document.get("original_bytes")
        if not original_bytes:
            raise RuntimeError(
                "Document has no original_bytes; cannot render "
                "without a source PDF to preserve."
            )

        current_pages = document.get("pages") or []
        baseline_pages = document.get("original_pages") or []

        ops = self._build_ops(current_pages, baseline_pages)

        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.pdf"
            output_path = Path(tmp) / "output.pdf"

            input_path.write_bytes(original_bytes)
            ops_json = json.dumps(ops)

            command = [
                self.mutool, "run", str(self.SCRIPT_PATH),
                str(input_path), ops_json, str(output_path),
            ]

            result = subprocess.run(
                command, capture_output=True, text=True,
            )

            if result.returncode != 0 or "RENDER_OK" not in result.stdout:
                raise RuntimeError(
                    "mutool overlay render failed for "
                    + repr(output_name) + ": "
                    + (result.stderr or result.stdout)
                )

            return output_path.read_bytes()

    @staticmethod
    def _build_ops(current_pages, baseline_pages):
        baseline_by_page = {}
        for p in baseline_pages:
            baseline_by_page[p.get("number")] = p

        pages_ops = []

        for page in current_pages:
            page_number = page.get("number")
            baseline_page = baseline_by_page.get(page_number, {})

            baseline_elements = {}
            for e in (baseline_page.get("elements") or []):
                if e.get("type") == "text":
                    baseline_elements[e.get("id")] = e

            current_elements = {}
            for e in (page.get("elements") or []):
                if e.get("type") == "text":
                    current_elements[e.get("id")] = e

            redact_rects = []
            text_inserts = []

            for element_id, element in current_elements.items():
                baseline_element = baseline_elements.get(element_id)

                is_new = baseline_element is None
                is_changed = (
                    baseline_element is not None
                    and baseline_element.get("content") != element.get("content")
                )

                if not is_new and not is_changed:
                    continue

                if is_changed:
                    x0 = baseline_element.get("x", 0)
                    y0 = baseline_element.get("y", 0)
                    width = baseline_element.get("width", 0)
                    height = baseline_element.get("height", 0)
                    redact_rects.append([x0, y0, x0 + width, y0 + height])

                page_height = page.get("height", 842)
                text_inserts.append({
                    "content": element.get("content", ""),
                    "x": element.get("x", 0),
                    "y": page_height - element.get("y", 0),
                    "font": element.get("font") or "Helvetica",
                    "font_size": element.get("font_size") or 12,
                    "color": element.get("color") or 0,
                })

            for element_id, baseline_element in baseline_elements.items():
                if element_id not in current_elements:
                    x0 = baseline_element.get("x", 0)
                    y0 = baseline_element.get("y", 0)
                    width = baseline_element.get("width", 0)
                    height = baseline_element.get("height", 0)
                    redact_rects.append([x0, y0, x0 + width, y0 + height])

            pages_ops.append({
                "page_index": (page_number - 1) if page_number else 0,
                "redact_rects": redact_rects,
                "text_inserts": text_inserts,
                "background_patches": [],
                "image_inserts": [],
            })

        return {"pages": pages_ops}
