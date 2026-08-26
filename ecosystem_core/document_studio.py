"""
CopySwiftAI™ Document Studio Foundation.
"""

from copy import deepcopy


class DocumentStudio:
    """Initial shared-kernel document inspection component."""

    def __init__(self, provider=None, importer=None, parser=None, renderer=None):
        self.provider = provider
        self.importer = importer
        self.parser = parser
        self.renderer = renderer

    def import_document(self, source):
        """Normalize a source document through the shared importer."""
        if self.importer is None:
            raise RuntimeError("Document importer is not configured.")
        return self.importer.normalize(source)

    def import_binary_document(self, data, file_name):
        """Parse binary document data and normalize it into the canonical model."""

        if self.parser is None:
            raise RuntimeError(
                "Document parser is not configured."
            )

        parsed = self.parser.parse(
            data,
            file_name=file_name,
        )

        return self.import_document(parsed)

    def render_document(self, document, output_name="output.pdf"):
        """Render a canonical document through the shared renderer."""

        if self.renderer is None:
            raise RuntimeError(
                "Document rendering engine is not configured."
            )

        return self.renderer.render(
            document,
            output_name=output_name,
        )

    def export_document(self, document, output_name="output.pdf"):
        """Render a canonical document through the shared renderer."""

        if self.renderer is None:
            raise RuntimeError(
                "Document rendering engine is not configured."
            )

        return self.renderer.render(
            document,
            output_name=output_name,
        )

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


    def find_element(self, document, element_id):
        """Return an element by ID without modifying the document."""

        if not isinstance(document, dict):
            return None

        target_id = str(element_id)

        for page in document.get("pages") or []:
            if not isinstance(page, dict):
                continue

            for element in page.get("elements") or []:
                if not isinstance(element, dict):
                    continue

                if str(element.get("id")) == target_id:
                    return element

        return None


    def move_element(self, document, element_id, x, y):
        """Return an edited copy with an element moved to a new position."""

        updated_document = deepcopy(document)

        if not isinstance(updated_document, dict):
            raise TypeError("Document must be a dictionary.")

        target_id = str(element_id)

        for page in updated_document.get("pages") or []:
            if not isinstance(page, dict):
                continue

            for element in page.get("elements") or []:
                if not isinstance(element, dict):
                    continue

                if str(element.get("id")) != target_id:
                    continue

                element["x"] = x
                element["y"] = y

                return updated_document

        raise KeyError(
            f"Element '{element_id}' was not found."
        )


    def resize_element(self, document, element_id, width, height):
        """Return an edited copy with an element resized."""

        updated_document = deepcopy(document)

        if not isinstance(updated_document, dict):
            raise TypeError("Document must be a dictionary.")

        target_id = str(element_id)

        for page in updated_document.get("pages") or []:
            if not isinstance(page, dict):
                continue

            for element in page.get("elements") or []:
                if not isinstance(element, dict):
                    continue

                if str(element.get("id")) != target_id:
                    continue

                element["width"] = width
                element["height"] = height

                return updated_document

        raise KeyError(
            f"Element '{element_id}' was not found."
        )


    def move_element_forward(self, document, element_id):
        """Return a copy with an element moved one position forward."""

        updated_document = deepcopy(document)

        if not isinstance(updated_document, dict):
            raise TypeError("Document must be a dictionary.")

        target_id = str(element_id)

        for page in updated_document.get("pages") or []:
            if not isinstance(page, dict):
                continue

            elements = page.get("elements") or []

            for index, element in enumerate(elements):
                if not isinstance(element, dict):
                    continue

                if str(element.get("id")) != target_id:
                    continue

                if index < len(elements) - 1:
                    elements[index], elements[index + 1] = (
                        elements[index + 1],
                        elements[index],
                    )

                return updated_document

        raise KeyError(
            f"Element '{element_id}' was not found."
        )

    def move_element_backward(self, document, element_id):
        """Return a copy with an element moved one position backward."""

        updated_document = deepcopy(document)

        if not isinstance(updated_document, dict):
            raise TypeError("Document must be a dictionary.")

        target_id = str(element_id)

        for page in updated_document.get("pages") or []:
            if not isinstance(page, dict):
                continue

            elements = page.get("elements") or []

            for index, element in enumerate(elements):
                if not isinstance(element, dict):
                    continue

                if str(element.get("id")) != target_id:
                    continue

                if index > 0:
                    elements[index], elements[index - 1] = (
                        elements[index - 1],
                        elements[index],
                    )

                return updated_document

        raise KeyError(
            f"Element '{element_id}' was not found."
        )

    def move_element_to_front(self, document, element_id):
        """Return a copy with an element moved to the top layer."""

        updated_document = deepcopy(document)

        if not isinstance(updated_document, dict):
            raise TypeError("Document must be a dictionary.")

        target_id = str(element_id)

        for page in updated_document.get("pages") or []:
            if not isinstance(page, dict):
                continue

            elements = page.get("elements") or []

            for index, element in enumerate(elements):
                if not isinstance(element, dict):
                    continue

                if str(element.get("id")) != target_id:
                    continue

                if index < len(elements) - 1:
                    elements.append(elements.pop(index))

                return updated_document

        raise KeyError(
            f"Element '{element_id}' was not found."
        )

    def move_element_to_back(self, document, element_id):
        """Return a copy with an element moved to the bottom layer."""

        updated_document = deepcopy(document)

        if not isinstance(updated_document, dict):
            raise TypeError("Document must be a dictionary.")

        target_id = str(element_id)

        for page in updated_document.get("pages") or []:
            if not isinstance(page, dict):
                continue

            elements = page.get("elements") or []

            for index, element in enumerate(elements):
                if not isinstance(element, dict):
                    continue

                if str(element.get("id")) != target_id:
                    continue

                if index > 0:
                    elements.insert(0, elements.pop(index))

                return updated_document

        raise KeyError(
            f"Element '{element_id}' was not found."
        )


    def duplicate_element(
        self,
        document,
        element_id,
        new_element_id,
        x,
        y,
    ):
        """Return a copy with a duplicated element at a new position."""

        updated_document = deepcopy(document)

        if not isinstance(updated_document, dict):
            raise TypeError("Document must be a dictionary.")

        source_id = str(element_id)
        target_id = str(new_element_id)

        for page in updated_document.get("pages") or []:
            if not isinstance(page, dict):
                continue

            elements = page.get("elements") or []

            if any(
                isinstance(element, dict)
                and str(element.get("id")) == target_id
                for element in elements
            ):
                raise ValueError(
                    f"Element '{new_element_id}' already exists."
                )

            for element in elements:
                if not isinstance(element, dict):
                    continue

                if str(element.get("id")) != source_id:
                    continue

                duplicate = deepcopy(element)
                duplicate["id"] = target_id
                duplicate["x"] = x
                duplicate["y"] = y

                elements.append(duplicate)
                return updated_document

        raise KeyError(
            f"Element '{element_id}' was not found."
        )


    def delete_element(self, document, element_id):
        """Return an edited copy with one element removed."""

        updated_document = deepcopy(document)

        if not isinstance(updated_document, dict):
            raise TypeError("Document must be a dictionary.")

        target_id = str(element_id)

        for page in updated_document.get("pages") or []:
            if not isinstance(page, dict):
                continue

            elements = page.get("elements") or []

            for index, element in enumerate(elements):
                if not isinstance(element, dict):
                    continue

                if str(element.get("id")) != target_id:
                    continue

                del elements[index]
                return updated_document

        raise KeyError(
            f"Element '{element_id}' was not found."
        )


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


    def edit_text_style(self, document, element_id, font=None, font_size=None, color=None):
        """Return an edited copy with selected text style metadata updated."""
        updated_document = deepcopy(document)
        if not isinstance(updated_document, dict):
            raise TypeError("Document must be a dictionary.")
        target_id = str(element_id)
        for page in updated_document.get("pages") or []:
            if not isinstance(page, dict):
                continue
            for element in page.get("elements") or []:
                if not isinstance(element, dict):
                    continue
                if str(element.get("id")) != target_id:
                    continue
                if str(element.get("type", "")).lower() != "text":
                    raise ValueError("Only text elements can be styled by edit_text_style().")
                if font is not None:
                    element["font"] = font
                if font_size is not None:
                    element["font_size"] = font_size
                if color is not None:
                    element["color"] = color
                return updated_document
        raise KeyError(f"Text element \{element_id}\ was not found.")

    def edit_image(self, document, element_id, image_data):
        """Return an edited copy with replacement image binary data."""

        updated_document = deepcopy(document)

        if not isinstance(updated_document, dict):
            raise TypeError("Document must be a dictionary.")

        target_id = str(element_id)

        for page in updated_document.get("pages") or []:
            if not isinstance(page, dict):
                continue

            for element in page.get("elements") or []:
                if not isinstance(element, dict):
                    continue

                if str(element.get("id")) != target_id:
                    continue

                if str(element.get("type", "")).lower() != "image":
                    raise ValueError(
                        "Only image elements can be edited by edit_image()."
                    )

                element["image_data"] = image_data
                return updated_document

        raise KeyError(
            f"Image element '{element_id}' was not found."
        )


    def add_image(
        self,
        document,
        page_number,
        element_id,
        image_data,
        x,
        y,
        width,
        height,
        image_format=None,
    ):
        """Return a copy with a new positioned image element."""

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
                    "type": "image",
                    "image_data": image_data,
                    "image_format": image_format,
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
