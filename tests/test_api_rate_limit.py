import unittest

from payment_engine.rate_limit import RateLimiter
from payment_engine.exceptions import ValidationError


class ApiRateLimitTests(unittest.TestCase):

    def test_limit_exceeded(self):
        limiter = RateLimiter(limit=1, window=60)

        limiter.check("api-client")

        with self.assertRaises(ValidationError):
            limiter.check("api-client")

    def test_different_clients(self):
        limiter = RateLimiter(limit=1, window=60)

        limiter.check("client-a")

        self.assertTrue(limiter.check("client-b"))


if __name__ == "__main__":
    unittest.main()
