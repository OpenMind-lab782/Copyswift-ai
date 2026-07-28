from payment_engine.registry import GatewayRegistry

from payment_engine.gateways.crypto import CryptoGateway
from payment_engine.gateways.paystack import PaystackGateway
from payment_engine.gateways.flutterwave import FlutterwaveGateway
from payment_engine.gateways.dpo import DPOGateway


class PaymentEngine:

    VERSION = "1.2.0"

    def __init__(self):
        self.registry = GatewayRegistry()

        self.registry.register(CryptoGateway())
        self.registry.register(PaystackGateway())
        self.registry.register(FlutterwaveGateway())
        self.registry.register(DPOGateway())

    def gateways(self):
        return self.registry.list()

    def get_gateway(self, name):
        gateway = self.registry.get(name)

        if gateway is None:
            raise ValueError(f"Unknown gateway: {name}")

        return gateway



    def submit_payment(self, request):
        gateway = self.get_gateway(request.gateway)

        return gateway.initialize_payment(
            request.amount,
            request.currency,
            request.customer
        )
    def create_payment(
        self,
        gateway,
        amount,
        currency,
        customer
    ):
        return self.get_gateway(gateway).initialize_payment(
            amount,
            currency,
            customer
        )

    def verify_payment(
        self,
        gateway,
        reference
    ):
        return self.get_gateway(gateway).verify_payment(
            reference
        )

    def refund_payment(
        self,
        gateway,
        reference
    ):
        return self.get_gateway(gateway).refund_payment(
            reference
        )

    def handle_webhook(
        self,
        gateway,
        payload
    ):
        return self.get_gateway(gateway).handle_webhook(
            payload
        )
