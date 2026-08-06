from typing import Any, Dict

from payment_engine.registry import GatewayRegistry
from payment_engine.logger import log_payment_event, log_error


class WebhookManager:

    def __init__(self):
        self.registry = GatewayRegistry()

    def process(self, gateway_name: str, payload: Dict[str, Any]):
        gateway = self.registry.get(gateway_name)

        try:
            result = gateway.handle_webhook(payload)

            log_payment_event(
                "webhook_processed",
                gateway=gateway_name
            )

            return result

        except Exception as e:
            log_error(
                "webhook_failed",
                gateway=gateway_name,
                error=str(e)
            )
            raise
