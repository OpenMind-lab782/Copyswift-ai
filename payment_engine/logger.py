import logging
from pathlib import Path


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "swift_payment_engine.log"


logger = logging.getLogger("SwiftPaymentEngine")

if not logger.handlers:
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


_SENSITIVE_LOG_FIELDS = {
    "authorization_url",
    "access_code",
    "customer",
}


def _redact_log_value(key, value):
    if key in _SENSITIVE_LOG_FIELDS:
        return "[REDACTED]"
    return value


def _format_log_details(kwargs):
    return " | ".join(
        f"{k}={_redact_log_value(k, v)}" for k, v in kwargs.items()
    )


def log_payment_event(event, **kwargs):
    logger.info(f"{event} | {_format_log_details(kwargs)}")


def log_error(event, error, **kwargs):
    details = _format_log_details(kwargs)
    logger.error(f"{event} | {details} | error={error}")
