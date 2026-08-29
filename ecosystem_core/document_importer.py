"""
CopySwiftAI™ Document Importer Foundation.
"""
from copy import deepcopy
class DocumentImporter:
    """Normalizes supported document representations into a canonical model."""
    _SUPPORTED_FORMATS = ("pdf", "docx")
    def __init__(self):
        pass
    def supported_formats(self):
        """Return document formats supported by the importer layer."""
        return list(self._SUPPORTED_FORMATS)
    def normalize(self, source):
        """Normalize a document representation without mutating the source."""
        if not isinstance(source, dict):
            raise TypeError("Document source must be a dictionary.")
        normalized = deepcopy(source)
        pages = normalized.get("pages") or []
        canonical_pages = []
        for index, page in enumerate(pages, start=1):
            if not isinstance(page, dict):
                continue
            elements = page.get("elements") or []
            canonical_elements = []
            for element_index, element in enumerate(elements, start=1):
                if not isinstance(element, dict):
                    continue
                item = dict(element)
                item.setdefault(
                    "id",
                    f"element-{index}-{element_index}",
                )
                item.setdefault("type", "unknown")
                item.setdefault("content", "")
                item.setdefault("x", 0)
                item.setdefault("y", 0)
                item.setdefault("width", 0)
                item.setdefault("height", 0)
                canonical_elements.append(item)
            canonical_pages.append(
                {
                    "number": page.get("number", index),
                    "width": page.get("width"),
                    "height": page.get("height"),
                    "elements": canonical_elements,
                }
            )
        name = str(
            normalized.get("name", "")
        ).strip()
        return {
            "name": name,
            "page_count": len(canonical_pages),
            "pages": canonical_pages,
            "original_pages": normalized.get("original_pages"),
            "original_bytes": normalized.get("original_bytes"),
            "original_sha256": normalized.get("original_sha256"),
            "metadata": {
                "source_format": self._detect_format(name),
                "normalized": True,
            },
        }
    @staticmethod
    def _detect_format(name):
        suffix = name.lower().rsplit(".", 1)[-1] if "." in name else ""
        return suffix or "unknown"
