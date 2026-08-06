import unittest


class PaymentFlowIntegrationTests(unittest.TestCase):

    def test_payment_flow_components_available(self):
        from payment_engine.gateway.adaptive_engine import AdaptiveRoutingEngine
        from payment_engine.gateway.webhook_signature import WebhookSignatureVerifier
        from payment_engine.middleware.idempotency import IdempotencyStore

        self.assertIsNotNone(AdaptiveRoutingEngine)
        self.assertIsNotNone(WebhookSignatureVerifier)
        self.assertIsNotNone(IdempotencyStore)


if __name__ == "__main__":
    unittest.main()
