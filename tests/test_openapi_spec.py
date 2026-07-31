import unittest

from payment_engine.api.openapi import openapi_spec


class OpenApiSpecTests(unittest.TestCase):

    def test_endpoint_exists(self):
        self.assertTrue(callable(openapi_spec))


if __name__ == "__main__":
    unittest.main()
