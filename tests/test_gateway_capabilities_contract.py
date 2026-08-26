import unittest

from payment_engine.gateway_capabilities import GatewayCapabilities
from payment_engine.gateways.crypto import CryptoGateway
from payment_engine.gateways.dpo import DPOGateway
from payment_engine.gateways.flutterwave import FlutterwaveGateway
from payment_engine.gateways.paystack import PaystackGateway


class GatewayCapabilitiesContractTests(unittest.TestCase):

    def test_default_capabilities_are_false(self):
        capabilities = GatewayCapabilities()

        self.assertFalse(capabilities.supports_cards)
        self.assertFalse(capabilities.supports_bank_transfer)
        self.assertFalse(capabilities.supports_mobile_money)
        self.assertFalse(capabilities.supports_crypto)
        self.assertFalse(capabilities.supports_refunds)
        self.assertFalse(capabilities.supports_webhooks)

    def test_paystack_refund_capability(self):
        gateway = PaystackGateway()

        self.assertTrue(
            gateway.capabilities.supports_refunds
        )

        self.assertFalse(
            gateway.capabilities.supports_crypto
        )

    def test_flutterwave_refund_capability(self):
        gateway = FlutterwaveGateway()

        self.assertTrue(
            gateway.capabilities.supports_refunds
        )

    def test_crypto_capability(self):
        gateway = CryptoGateway()

        self.assertTrue(
            gateway.capabilities.supports_crypto
        )

        self.assertFalse(
            gateway.capabilities.supports_refunds
        )

    def test_dpo_capabilities(self):
        gateway = DPOGateway()

        self.assertTrue(
            gateway.capabilities.supports_cards
        )

        self.assertTrue(
            gateway.capabilities.supports_bank_transfer
        )

        self.assertFalse(
            gateway.capabilities.supports_refunds
        )


if __name__ == "__main__":
    unittest.main()
