"""
CopySwiftAI™ Document Adapter Registry.
"""


class DocumentAdapterRegistry:
    """Registers and resolves optional document-engine adapters."""

    _SUPPORTED_FORMATS = ("pdf", "docx")

    def __init__(self):
        self._adapters = {}

    def register(self, file_format, adapter):
        normalized_format = str(file_format or "").strip().lower()

        if normalized_format not in self._SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported document format: "
                f"{normalized_format or 'unknown'}"
            )

        if not hasattr(adapter, "parse") or not callable(adapter.parse):
            raise TypeError(
                "Document adapter must expose a callable parse() method."
            )

        self._adapters[normalized_format] = adapter

    def get(self, file_format):
        normalized_format = str(file_format or "").strip().lower()
        return self._adapters.get(normalized_format)

    def list_formats(self):
        return sorted(self._adapters.keys())

    def exists(self, file_format):
        normalized_format = str(file_format or "").strip().lower()
        return normalized_format in self._adapters
