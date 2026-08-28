"""
CopySwiftAI Document Studio - Immutable overlay renderer.

Preserves the original PDF content, style, and background completely
unchanged. Only text/images that were actually added or edited by the
user are redacted (text-only redaction; images are simply left alone
unless deleted) and redrawn; everything else in the source PDF is
left byte-for-byte untouched.
"""

import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
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

        computed_hash = hashlib.sha256(original_bytes).hexdigest()
        stored_hash = document.get("original_sha256")
        if stored_hash and stored_hash != computed_hash:
            raise RuntimeError(
                "Integrity check failed: original_bytes no longer "
                "matches the hash recorded at import time. Refusing "
                "to render, since the immutability guarantee cannot "
                "be confirmed."
            )

        current_pages = document.get("pages") or []
        baseline_pages = document.get("original_pages") or []

        ops = self._build_ops(current_pages, baseline_pages)
        ops["audit"] = {
            "original_sha256": computed_hash,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

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

            baseline_text = {}
            baseline_images = {}
            for e in (baseline_page.get("elements") or []):
                if e.get("type") == "text":
                    baseline_text[e.get("id")] = e
                elif e.get("type") == "image":
                    baseline_images[e.get("id")] = e

            current_text = {}
            current_images = {}
            for e in (page.get("elements") or []):
                if e.get("type") == "text":
                    current_text[e.get("id")] = e
                elif e.get("type") == "image":
                    current_images[e.get("id")] = e

            redact_rects_text = []
            redact_rects_image = []
            text_inserts = []
            image_inserts = []

            page_height = page.get("height", 842)

            # --- text diffing ---
            for element_id, element in current_text.items():
                baseline_element = baseline_text.get(element_id)

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
                    redact_rects_text.append([x0, y0, x0 + width, y0 + height])

                text_inserts.append({
                    "content": element.get("content", ""),
                    "x": element.get("x", 0),
                    "y": page_height - element.get("y", 0),
                    "font": element.get("font") or "Helvetica",
                    "font_size": element.get("font_size") or 12,
                    "color": element.get("color") or 0,
                })

            for element_id, baseline_element in baseline_text.items():
                if element_id not in current_text:
                    x0 = baseline_element.get("x", 0)
                    y0 = baseline_element.get("y", 0)
                    width = baseline_element.get("width", 0)
                    height = baseline_element.get("height", 0)
                    redact_rects_text.append([x0, y0, x0 + width, y0 + height])

            # --- image diffing ---
            # Images are only ever added or removed wholesale (never
            # "edited in place") since they are opaque binary content.
            # A changed image is modeled as delete-old + add-new.
            for element_id, element in current_images.items():
                baseline_element = baseline_images.get(element_id)

                is_new = baseline_element is None
                is_changed = (
                    baseline_element is not None
                    and baseline_element.get("image_data_base64")
                        != element.get("image_data_base64")
                )

                if not is_new and not is_changed:
                    continue

                if is_changed:
                    x0 = baseline_element.get("x", 0)
                    y0 = baseline_element.get("y", 0)
                    width = baseline_element.get("width", 0)
                    height = baseline_element.get("height", 0)
                    # Image y is the literal PDF bottom-up coordinate
                    # (unlike text, which is true top-down) - setRect()
                    # needs a page-height-relative flip for this to
                    # actually intersect the image region correctly.
                    redact_rects_image.append([
                        x0, page_height - y0 - height,
                        x0 + width, page_height - y0,
                    ])

                x = element.get("x", 0)
                y = element.get("y", 0)
                width = element.get("width", 0)
                height = element.get("height", 0)

                # Note: unlike text, the literal PDF y written here is
                # passed straight through (not page_height - y - height).
                # apply_overlay.js writes this directly as a raw content
                # stream operator, bypassing the pre-flip convention that
                # MuPDF's page.run() device callback applies when READING
                # images back out (which is what extract_images.js
                # compensates for). Passing y through directly here is
                # what makes a later re-extraction report the same y.
                image_inserts.append({
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "png_base64": element.get("image_data_base64", ""),
                })

            for element_id, baseline_element in baseline_images.items():
                if element_id not in current_images:
                    x0 = baseline_element.get("x", 0)
                    y0 = baseline_element.get("y", 0)
                    width = baseline_element.get("width", 0)
                    height = baseline_element.get("height", 0)
                    redact_rects_image.append([
                        x0, page_height - y0 - height,
                        x0 + width, page_height - y0,
                    ])

            pages_ops.append({
                "page_index": (page_number - 1) if page_number else 0,
                "redact_rects_text": redact_rects_text,
                "redact_rects_image": redact_rects_image,
                "text_inserts": text_inserts,
                "background_patches": [],
                "image_inserts": image_inserts,
            })

        return {"pages": pages_ops}
