import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


class NativeMuPDFAdapter:
    """PDF parser backed by Termux native mutool."""

    IMAGE_SCRIPT_PATH = Path(__file__).parent.parent / "mutool_scripts" / "extract_images.js"

    def __init__(self):
        self.mutool = shutil.which("mutool")

    def parse(self, data, file_name):
        mutool = shutil.which("mutool")
        if not mutool:
            raise RuntimeError("Native MuPDF mutool is unavailable.")

        name = str(file_name or "").strip()

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.pdf"
            output = Path(tmp) / "source.stext"
            source.write_bytes(data)

            command = [mutool, "draw", "-F", "stext", "-o", str(output), str(source)]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                root = ET.parse(output).getroot()
            except Exception as exc:
                raise RuntimeError(f"Native MuPDF could not parse {name!r}.") from exc

            images_by_page = {}
            if self.mutool and self.IMAGE_SCRIPT_PATH.exists():
                try:
                    image_command = [
                        self.mutool, "run", str(self.IMAGE_SCRIPT_PATH), str(source),
                    ]
                    image_result = subprocess.run(
                        image_command, capture_output=True, text=True, check=True,
                    )
                    image_data = json.loads(image_result.stdout)
                    for page_entry in image_data.get("pages", []):
                        images_by_page[page_entry["page_index"]] = page_entry.get("images", [])
                except Exception:
                    # Image extraction is best-effort; text extraction must not
                    # fail just because image extraction had a problem.
                    images_by_page = {}

        pages = []
        for page_index, page_node in enumerate(root.findall("page"), 1):
            elements = []

            for block_index, block_node in enumerate(page_node.findall("block"), 1):
                text = "".join(
                    char.get("c", "") for char in block_node.findall(".//char")
                ).strip()
                if not text:
                    continue
                font_node = block_node.find(".//font")
                font_size = (
                    float(font_node.get("size"))
                    if font_node is not None and font_node.get("size")
                    else None
                )
                color = None
                if font_node is not None:
                    first_char = font_node.find(".//char")
                    if first_char is not None:
                        color = first_char.get("color")
                bbox = (block_node.get("bbox") or "0 0 0 0").split()
                x0, y0, x1, y1 = [float(value) for value in bbox[:4]]
                elements.append({
                    "id": f"page-{page_index}-block-{block_index}",
                    "type": "text",
                    "content": text,
                    "x": x0,
                    "y": y0,
                    "width": max(0, x1 - x0),
                    "height": max(0, y1 - y0),
                    "font": font_node.get("name") if font_node is not None else None,
                    "font_size": font_size,
                    "color": color,
                })

            page_images = images_by_page.get(page_index - 1, [])
            for image_index, image_entry in enumerate(page_images, 1):
                elements.append({
                    "id": f"page-{page_index}-image-{image_index}",
                    "type": "image",
                    "x": image_entry.get("x", 0),
                    "y": image_entry.get("y", 0),
                    "width": image_entry.get("width", 0),
                    "height": image_entry.get("height", 0),
                    "image_format": "png",
                    "image_data_base64": image_entry.get("png_base64"),
                })

            pages.append({
                "number": page_index,
                "width": float(page_node.get("width") or 0),
                "height": float(page_node.get("height") or 0),
                "elements": elements,
            })

        return {
            "name": name,
            "pages": pages,
            "original_pages": copy.deepcopy(pages),
            "original_bytes": data,
            "original_sha256": hashlib.sha256(data).hexdigest(),
            "metadata": {"source_format": "pdf", "parser_engine": "native-mupdf"},
        }
