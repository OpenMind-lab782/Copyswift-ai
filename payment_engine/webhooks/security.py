import hmac
import hashlib


def verify_signature(secret, payload, signature):
    """
    Verify an HMAC-SHA256 webhook signature.
    """
    expected = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
