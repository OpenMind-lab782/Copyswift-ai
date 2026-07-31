from dataclasses import dataclass
import os

from .settings import Settings

settings = Settings()


@dataclass(frozen=True)
class EngineConfig:
    """Backward-compatible engine configuration."""

    retry_attempts: int = 3
    retry_delay: float = 0.0

    timeout_seconds: float = 5.0

    circuit_failure_threshold: int = 3
    circuit_recovery_timeout: float = 30.0

    enable_metrics: bool = True
    enable_events: bool = True
    enable_middleware: bool = True

    @property
    def environment(self):
        return settings.environment

    @property
    def database(self):
        return settings.database

    @property
    def gateway_mode(self):
        return settings.gateway_mode

    @property
    def log_level(self):
        return settings.log_level
