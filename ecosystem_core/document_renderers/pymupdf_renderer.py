"""
CopySwiftAI™ PyMuPDF Document Renderer.
"""


class PyMuPDFRenderer:
    """Optional PDF renderer backed by PyMuPDF."""

    def __init__(self):
        self._engine = None
        self._load_error = None

        try:
            import fitz
        except ImportError as exc:
            self._load_error = exc
        else:
            self._engine = fitz

    def render(self, document, output_name="output.pdf"):
        """Render a canonical document model into PDF bytes."""

        if not isinstance(document, dict):
            raise TypeError("Document must be a dictionary.")

        if self._engine is None:
            raise RuntimeError(
                "PyMuPDF PDF rendering engine is unavailable."
            ) from self._load_error

        try:
            pdf = self._engine.open()

            for page_data in document.get("pages") or []:
                width = float(page_data.get("width") or 595)
                height = float(page_data.get("height") or 842)

                page = pdf.new_page(
                    width=width,
                    height=height,
                )

                for element in page_data.get("elements") or []:
                    element_type = str(
                        element.get("type", "")
                    ).strip().lower()

                    if element_type == "text":
                        page.insert_text(
                            (
                                float(element.get("x", 0)),
                                float(element.get("y", 0)),
                            ),
                            str(element.get("content", "")),
                            fontname=element.get("font") or "helv",
                            fontsize=float(
                                element.get("font_size") or 12
                            ),
                            color=self._color_to_rgb(
                                element.get("color", 0)
                            ),
                        )

                    elif element_type == "image":
                        image_data = element.get("image_data")

                        if image_data is None:
                            continue

                        rect = self._engine.Rect(
                            float(element.get("x", 0)),
                            float(element.get("y", 0)),
                            float(element.get("x", 0))
                            + float(element.get("width", 0)),
                            float(element.get("y", 0))
                            + float(element.get("height", 0)),
                        )

                        page.insert_image(
                            rect,
                            stream=image_data,
                        )

            payload = pdf.tobytes()
            pdf.close()

            return payload

        except Exception as exc:
            raise RuntimeError(
                f"PyMuPDF could not render '{output_name}'."
            ) from exc

    @staticmethod
    def _color_to_rgb(color):
        if not isinstance(color, int):
            return (0, 0, 0)

        red = ((color >> 16) & 255) / 255
        green = ((color >> 8) & 255) / 255
        blue = (color & 255) / 255

        return (red, green, blue)
