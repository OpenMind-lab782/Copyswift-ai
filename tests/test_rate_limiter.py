import unittest

from payment_engine.exceptions import ValidationError
from payment_engine.rate_limit import RateLimiter


class RateLimiterTests(unittest.TestCase):

    def test_request_allowed(self):
        limiter = RateLimiter(limit=2, window=60)

        self.assertTrue(limiter.check("client-1"))

    def test_rate_limit_exceeded(self):
        limiter = RateLimiter(limit=2, window=60)

        limiter.check("client-1")
        limiter.check("client-1")

        with self.assertRaises(ValidationError):
            limiter.check("client-1")

    def test_different_clients(self):
        limiter = RateLimiter(limit=1, window=60)

        limiter.check("client-a")

        self.assertTrue(
            limiter.check("client-b")
        )


if __name__ == "__main__":
    unittest.main()
