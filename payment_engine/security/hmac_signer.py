import hmac
import hashlib


class HMACSigner:
    """
    HMAC request signing utility.
    """

    def __init__(self, secret):
        self.secret = secret.encode("utf-8")

    def sign(self, message):
        return hmac.new(
            self.secret,
            message.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def verify(self, message, signature):
        expected = self.sign(message)

        return hmac.compare_digest(
            expected,
            signature
        )
