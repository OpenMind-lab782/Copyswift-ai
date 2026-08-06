from payment_engine.gateways.crypto import CryptoGateway
from payment_engine.gateways.paystack import PaystackGateway
from payment_engine.gateways.flutterwave import FlutterwaveGateway
from payment_engine.gateways.dpo import DPOGateway


class GatewayFactory:
    """
    Creates gateway instances by provider name.
    """

    _gateways = {
        "crypto": CryptoGateway,
        "paystack": PaystackGateway,
        "flutterwave": FlutterwaveGateway,
        "dpo": DPOGateway,
    }

    @classmethod
    def create(cls, gateway_name):
        gateway = cls._gateways.get(gateway_name)

        if gateway is None:
            raise ValueError(f"Unknown gateway: {gateway_name}")

        return gateway()

    @classmethod
    def supported_gateways(cls):
        return sorted(cls._gateways.keys())
