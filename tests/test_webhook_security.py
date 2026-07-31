import hashlib
import hmac
import unittest

from payment_engine.webhooks import verify_signature


class WebhookSecurityTests(unittest.TestCase):

    def test_valid_signature(self):
        secret = "secret123"
        payload = b'{"event":"payment.success"}'

        signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        self.assertTrue(
            verify_signature(
                secret,
                payload,
                signature,
            )
        )

    def test_invalid_signature(self):
        self.assertFalse(
            verify_signature(
                "secret123",
                b"{}",
                "invalid",
            )
        )


if __name__ == "__main__":
    unittest.main()
