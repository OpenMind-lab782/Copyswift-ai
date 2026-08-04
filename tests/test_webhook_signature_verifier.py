import hashlib
import hmac
import unittest

from payment_engine.gateway.webhook_signature import (
    WebhookSignatureVerifier,
)


class WebhookSignatureVerifierTests(unittest.TestCase):

    def setUp(self):
        self.secret = "secret-key"

        self.verifier = WebhookSignatureVerifier(
            self.secret
        )

    def test_valid_signature(self):
        payload = b'{"status":"success"}'

        signature = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha512,
        ).hexdigest()

        self.assertTrue(
            self.verifier.verify(
                payload,
                signature,
            )
        )

    def test_invalid_signature(self):
        payload = b'{"status":"success"}'

        self.assertFalse(
            self.verifier.verify(
                payload,
                "invalid-signature",
            )
        )


if __name__ == "__main__":
    unittest.main()
