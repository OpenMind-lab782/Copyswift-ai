"""
CopySwiftAI™ Document Parser Adapter Foundation.
"""


class DocumentParser:
    """Stable adapter boundary for future PDF/DOCX parsing engines."""

    _SUPPORTED_FORMATS = ("pdf", "docx")

    def __init__(self, adapters=None):
        self.adapters = adapters or {}

    def supported_formats(self):
        """Return formats exposed by the parser boundary."""
        return list(self._SUPPORTED_FORMATS)

    def parse(self, data, file_name):
        """Parse binary document data through a format-specific adapter."""

        name = str(file_name or "").strip()
        extension = (
            name.lower().rsplit(".", 1)[-1]
            if "." in name
            else ""
        )

        if extension not in self._SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported document format: {extension or 'unknown'}"
            )

        adapter = self.adapters.get(extension)

        if adapter is None:
            raise RuntimeError(
                f"No parser adapter is configured for '{extension}'."
            )

        return adapter.parse(
            data,
            file_name=name,
        )
