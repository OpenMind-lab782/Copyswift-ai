import copy
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

class NativeMuPDFAdapter:
    """PDF parser backed by Termux native mutool."""
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
        pages = []
        for page_index, page_node in enumerate(root.findall("page"), 1):
            elements = []
            for block_index, block_node in enumerate(page_node.findall("block"), 1):
                text = "".join(char.get("c", "") for char in block_node.findall(".//char")).strip()
                if not text:
                    continue
                font_node = block_node.find(".//font")
                font_size = float(font_node.get("size")) if font_node is not None and font_node.get("size") else None
                color = None
                if font_node is not None:
                    first_char = font_node.find(".//char")
                    if first_char is not None:
                        color = first_char.get("color")
                bbox = (block_node.get("bbox") or "0 0 0 0").split()
                x0, y0, x1, y1 = [float(value) for value in bbox[:4]]
                elements.append({"id": f"page-{page_index}-block-{block_index}", "type": "text", "content": text, "x": x0, "y": y0, "width": max(0, x1 - x0), "height": max(0, y1 - y0), "font": font_node.get("name") if font_node is not None else None, "font_size": font_size, "color": color})
            pages.append({"number": page_index, "width": float(page_node.get("width") or 0), "height": float(page_node.get("height") or 0), "elements": elements})
        return {"name": name, "pages": pages, "original_pages": copy.deepcopy(pages), "original_bytes": data, "metadata": {"source_format": "pdf", "parser_engine": "native-mupdf"}}
