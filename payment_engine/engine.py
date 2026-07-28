from payment_engine.registry import GatewayRegistry

from payment_engine.gateways.crypto import CryptoGateway
from payment_engine.gateways.paystack import PaystackGateway
from payment_engine.gateways.flutterwave import FlutterwaveGateway
from payment_engine.gateways.dpo import DPOGateway

registry = GatewayRegistry()

registry.register(CryptoGateway())
registry.register(PaystackGateway())
registry.register(FlutterwaveGateway())
registry.register(DPOGateway())

class PaymentEngine:

    VERSION = "1.1.0"

    def gateways(self):
        return registry.list()

    def gateway(self, name):
        return registry.get(name)
