"""
Swift Payment Engine Configuration Package.

Provides the legacy EngineConfig alongside the newer Settings
configuration system and ConfigurationValidator.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from .settings import Settings
from .validator import ConfigurationValidator

_legacy_path = Path(__file__).resolve().parent.parent / "config.py"

_spec = spec_from_file_location(
    "_swift_payment_engine_legacy_config",
    _legacy_path,
)

_legacy_config = module_from_spec(_spec)
_spec.loader.exec_module(_legacy_config)

EngineConfig = _legacy_config.EngineConfig

settings = Settings()

__all__ = [
    "EngineConfig",
    "Settings",
    "settings",
    "ConfigurationValidator",
]
