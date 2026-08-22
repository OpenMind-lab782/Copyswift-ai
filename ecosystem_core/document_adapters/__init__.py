"""
CopySwiftAI™ Document Adapter Registry.
"""

from .registry import DocumentAdapterRegistry
from .native_mupdf_adapter import NativeMuPDFAdapter

__all__ = ["DocumentAdapterRegistry", "NativeMuPDFAdapter"]
