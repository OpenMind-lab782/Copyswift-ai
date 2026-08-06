from payment_engine.gateways.mock import MockGateway
from payment_engine.gateways.paystack import PaystackGateway
from payment_engine.gateways.flutterwave import FlutterwaveGateway
from payment_engine.gateways.stripe import StripeGateway
from payment_engine.gateways.paypal import PayPalGateway


class GatewayRegistry:

    _gateways = {
        "mock": MockGateway,
        "paystack": PaystackGateway,
        "flutterwave": FlutterwaveGateway,
        "stripe": StripeGateway,
        "paypal": PayPalGateway,
    }

    @classmethod
    def register(cls, name, gateway_class):
        cls._gateways[name.lower()] = gateway_class

    @classmethod
    def get_gateway(cls, name):
        gateway = cls._gateways.get(name.lower())

        if gateway is None:
            raise ValueError(f"Unsupported gateway: {name}")

        return gateway()

    @classmethod
    def available_gateways(cls):
        return sorted(cls._gateways.keys())
