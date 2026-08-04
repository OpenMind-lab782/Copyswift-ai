import hashlib
import hmac


class WebhookSignatureVerifier:
    """
    Verifies HMAC SHA-512 webhook signatures.
    """

    def __init__(self, secret):
        self.secret = secret.encode()

    def verify(self, payload, signature):
        expected = hmac.new(
            self.secret,
            payload,
            hashlib.sha512,
        ).hexdigest()

        return hmac.compare_digest(
            expected,
            signature,
        )
