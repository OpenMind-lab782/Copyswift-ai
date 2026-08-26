from abc import ABC, abstractmethod
from payment_engine.gateway_capabilities import GatewayCapabilities


class BaseGateway(ABC):
    """
    Base class for every payment gateway.
    """

    @property
    @abstractmethod
    def name(self):
        pass


    @property
    def capabilities(self):
        return GatewayCapabilities()


    @abstractmethod
    def initialize_payment(self, amount, currency, customer, **kwargs):
        pass

    @abstractmethod
    def verify_payment(self, reference):
        pass

    @abstractmethod
    def refund_payment(self, reference, amount=None):
        pass

    @abstractmethod
    def health_check(self):
        pass

    def handle_webhook(self, payload):
        return {
            "status": "unsupported",
            "gateway": self.name,
            "message": "Webhook handling is not supported by this gateway.",
        }
