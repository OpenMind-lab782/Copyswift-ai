"""
CopySwiftAI™ Document Studio Foundation.
"""

from copy import deepcopy


class DocumentStudio:
    """Initial shared-kernel document inspection component."""

    def __init__(self, provider=None, importer=None, parser=None):
        self.provider = provider
        self.importer = importer
        self.parser = parser

    def import_document(self, source):
        """Normalize a source document through the shared importer."""
        if self.importer is None:
            raise RuntimeError("Document importer is not configured.")
        return self.importer.normalize(source)

    def inspect_document(self, document):
        """Inspect a normalized document representation without modifying it."""

        if not isinstance(document, dict):
            return {
                "name": "",
                "page_count": 0,
                "pages": [],
                "structure": {
                    "element_types": [],
                    "has_text": False,
                    "has_positioned_elements": False,
                },
            }

        name = str(document.get("name", "")).strip()
        pages = document.get("pages") or []

        normalized_pages = []
        element_types = set()
        has_text = False
        has_positioned_elements = False

        for index, page in enumerate(pages, start=1):
            if not isinstance(page, dict):
                continue

            elements = page.get("elements") or []
            normalized_elements = []

            for element in elements:
                if not isinstance(element, dict):
                    continue

                element_copy = dict(element)
                normalized_elements.append(element_copy)

                element_type = str(
                    element.get("type", "")
                ).strip().lower()

                if element_type:
                    element_types.add(element_type)

                if element_type == "text" and str(
                    element.get("content", "")
                ).strip():
                    has_text = True

                if all(
                    key in element
                    for key in ("x", "y", "width", "height")
                ):
                    has_positioned_elements = True

            page_number = page.get("number", index)

            normalized_pages.append(
                {
                    "number": page_number,
                    "width": page.get("width"),
                    "height": page.get("height"),
                    "elements": normalized_elements,
                }
            )

        return {
            "name": name,
            "page_count": len(normalized_pages),
            "pages": normalized_pages,
            "structure": {
                "element_types": sorted(element_types),
                "has_text": has_text,
                "has_positioned_elements": has_positioned_elements,
            },
        }


    def edit_text(self, document, element_id, new_content):
        """Return an edited copy while preserving document structure."""

        updated_document = deepcopy(document)

        if not isinstance(updated_document, dict):
            raise TypeError("Document must be a dictionary.")

        target_id = str(element_id)
        replacement = str(new_content)

        for page in updated_document.get("pages") or []:
            if not isinstance(page, dict):
                continue

            for element in page.get("elements") or []:
                if not isinstance(element, dict):
                    continue

                if str(element.get("id")) != target_id:
                    continue

                if str(element.get("type", "")).lower() != "text":
                    raise ValueError(
                        "Only text elements can be edited by edit_text()."
                    )

                element["content"] = replacement
                return updated_document

        raise KeyError(
            f"Text element '{element_id}' was not found."
        )


    def add_text(
        self,
        document,
        page_number,
        element_id,
        content,
        x,
        y,
        width,
        height,
    ):
        """Return a copy with a new positioned text element."""

        updated_document = deepcopy(document)

        if not isinstance(updated_document, dict):
            raise TypeError("Document must be a dictionary.")

        for page in updated_document.get("pages") or []:
            if not isinstance(page, dict):
                continue

            if page.get("number") != page_number:
                continue

            elements = page.setdefault("elements", [])

            if any(
                isinstance(element, dict)
                and str(element.get("id")) == str(element_id)
                for element in elements
            ):
                raise ValueError(
                    f"Element '{element_id}' already exists."
                )

            elements.append(
                {
                    "id": str(element_id),
                    "type": "text",
                    "content": str(content),
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                }
            )

            return updated_document

        raise KeyError(
            f"Page '{page_number}' was not found."
        )
