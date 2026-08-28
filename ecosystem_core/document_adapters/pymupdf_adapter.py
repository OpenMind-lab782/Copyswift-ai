import copy
"""
CopySwiftAI™ PyMuPDF PDF Adapter.
"""


class PyMuPDFAdapter:
    """Optional PDF adapter backed by PyMuPDF."""

    def __init__(self):
        self._engine = None
        self._load_error = None

        try:
            import fitz
        except ImportError as exc:
            self._load_error = exc
        else:
            self._engine = fitz

    def parse(self, data, file_name):
        """Parse PDF binary data into the shared document representation."""

        if self._engine is None:
            raise RuntimeError(
                "PyMuPDF PDF engine is unavailable."
            ) from self._load_error

        try:
            document = self._engine.open(
                stream=data,
                filetype="pdf",
            )
        except Exception as exc:
            raise RuntimeError(
                f"PyMuPDF could not open '{file_name}'."
            ) from exc

        try:
            pages = []

            for page_number, page in enumerate(document, start=1):
                rect = page.rect
                elements = []

                text_dict = page.get_text("dict")

                for block_index, block in enumerate(
                    text_dict.get("blocks", []),
                    start=1,
                ):
                    block_type = block.get("type")

                    if block_type == 0:
                        lines = block.get("lines", [])

                        for line_index, line in enumerate(
                            lines,
                            start=1,
                        ):
                            spans = line.get("spans", [])

                            for span_index, span in enumerate(
                                spans,
                                start=1,
                            ):
                                content = str(
                                    span.get("text", "")
                                ).strip()

                                if not content:
                                    continue

                                bbox = span.get(
                                    "bbox",
                                    (0, 0, 0, 0),
                                )

                                x0, y0, x1, y1 = bbox

                                elements.append(
                                    {
                                        "id": (
                                            f"page-{page_number}-"
                                            f"block-{block_index}-"
                                            f"line-{line_index}-"
                                            f"span-{span_index}"
                                        ),
                                        "type": "text",
                                        "content": content,
                                        "x": x0,
                                        "y": y0,
                                        "width": max(0, x1 - x0),
                                        "height": max(0, y1 - y0),
                                        "font": span.get("font"),
                                        "font_size": span.get("size"),
                                        "flags": span.get("flags"),
                                        "color": span.get("color"),
                                    }
                                )

                    elif block_type == 1:
                        bbox = block.get(
                            "bbox",
                            (0, 0, 0, 0),
                        )

                        x0, y0, x1, y1 = bbox

                        elements.append(
                            {
                                "id": (
                                    f"page-{page_number}-"
                                    f"block-{block_index}"
                                ),
                                "type": "image",
                                "x": x0,
                                "y": y0,
                                "width": max(0, x1 - x0),
                                "height": max(0, y1 - y0),
                                "image_format": block.get("ext"),
                                "xres": block.get("xres"),
                                "yres": block.get("yres"),
                                "image_data": block.get("image"),
                            }
                        )

                pages.append(
                    {
                        "number": page_number,
                        "width": rect.width,
                        "height": rect.height,
                        "elements": elements,
                    }
                )

            return {
                "name": str(file_name or "").strip(),
                "pages": pages,
                "original_pages": copy.deepcopy(pages),
                "original_bytes": data,
                "metadata": {
                    "source_format": "pdf",
                    "parser_engine": "pymupdf",
                },
            }
        finally:
            document.close()
