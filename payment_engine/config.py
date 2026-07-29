from dataclasses import dataclass


@dataclass(frozen=True)
class EngineConfig:
    """Central configuration for the payment engine."""

    retry_attempts: int = 3
    retry_delay: float = 0.0

    timeout_seconds: float = 5.0

    circuit_failure_threshold: int = 3
    circuit_recovery_timeout: float = 30.0

    enable_metrics: bool = True
    enable_events: bool = True
    enable_middleware: bool = True
