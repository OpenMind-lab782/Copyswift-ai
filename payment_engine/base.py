from abc import ABC, abstractmethod

class BaseGateway(ABC):
    name = "base"

    @abstractmethod
    def initialize_payment(self, amount, currency, customer):
        pass

    @abstractmethod
    def verify_payment(self, reference):
        pass

    @abstractmethod
    def refund_payment(self, reference):
        pass

    @abstractmethod
    def handle_webhook(self, payload):
        pass
