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


def log_payment_event(event, **kwargs):
    details = " | ".join(
        f"{k}={v}" for k, v in kwargs.items()
    )

    logger.info(f"{event} | {details}")


def log_error(event, error, **kwargs):
    details = " | ".join(
        f"{k}={v}" for k, v in kwargs.items()
    )

    logger.error(f"{event} | {details} | error={error}")
