from abc import ABC, abstractmethod


class BaseGateway(ABC):
    """
    Base class for every payment gateway.
    """

    @property
    @abstractmethod
    def name(self):
        pass

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
