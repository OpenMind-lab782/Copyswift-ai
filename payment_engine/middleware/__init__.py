"""
Swift Payment Engine Middleware Package

Compatibility layer exposing the legacy MiddlewareManager
while providing the new middleware package modules.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from .idempotency import IdempotencyStore

_legacy_path = Path(__file__).resolve().parent.parent / "middleware.py"

_spec = spec_from_file_location(
    "_legacy_middleware",
    _legacy_path,
)

_legacy = module_from_spec(_spec)
_spec.loader.exec_module(_legacy)

MiddlewareManager = _legacy.MiddlewareManager

__all__ = [
    "MiddlewareManager",
    "IdempotencyStore",
]
