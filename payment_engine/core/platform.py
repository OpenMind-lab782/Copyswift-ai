"""
Central platform configuration.
"""

from payment_engine.core.version import engine_info

PLATFORM_NAME = "CopySwiftAI"
COMPANY_NAME = "OpenMind Lab"
DEFAULT_CURRENCY = "USD"
API_VERSION = "v1"


def platform_info():
    info = engine_info()
    info.update({
        "company": COMPANY_NAME,
        "default_currency": DEFAULT_CURRENCY,
        "api_version": API_VERSION,
    })
    return info
