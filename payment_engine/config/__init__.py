"""
Swift Payment Engine Configuration Package

Compatibility layer exposing the legacy EngineConfig
while providing the new configuration modules.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from .validator import ConfigurationValidator

_legacy_path = Path(__file__).resolve().parent.parent / "config.py"

_spec = spec_from_file_location(
    "_legacy_config",
    _legacy_path,
)

_legacy = module_from_spec(_spec)
_spec.loader.exec_module(_legacy)

EngineConfig = _legacy.EngineConfig

__all__ = [
    "EngineConfig",
    "ConfigurationValidator",
]
