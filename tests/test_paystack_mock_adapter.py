import unittest

from payment_engine.gateways.adapters import PaystackMockAdapter


class PaystackMockAdapterTests(unittest.TestCase):

    def setUp(self):
        self.adapter = PaystackMockAdapter()

    def test_initialize_payment(self):
        result = self.adapter.initialize_payment(
            100,
            "NGN",
            {"email": "test@example.com"},
        )

        self.assertEqual(result["gateway"], "paystack")
        self.assertEqual(result["mode"], "mock")
        self.assertIn("authorization_url", result)

    def test_verify_payment(self):
        result = self.adapter.verify_payment("TEST-001")

        self.assertTrue(result["paid"])
        self.assertEqual(result["gateway"], "paystack")


if __name__ == "__main__":
    unittest.main()
