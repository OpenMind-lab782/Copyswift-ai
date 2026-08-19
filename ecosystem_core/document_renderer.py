"""
CopySwiftAI™ Document Renderer Foundation.
"""


class DocumentRenderer:
    """Initial boundary for rendering canonical documents to PDF."""

    def __init__(self, engine=None):
        self.engine = engine

    def render(self, document, output_name="output.pdf"):
        """Render a canonical document through the configured engine."""

        if not isinstance(document, dict):
            raise TypeError("Document must be a dictionary.")

        if self.engine is None:
            raise RuntimeError(
                "Document rendering engine is not configured."
            )

        return self.engine.render(
            document,
            output_name=output_name,
        )
