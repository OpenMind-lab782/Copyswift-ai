import unittest

from payment_engine.services.merchant_service import MerchantService


class ApiKeyRotationTests(unittest.TestCase):

    def setUp(self):
        self.service = MerchantService()

    def test_rotate_api_key(self):

        merchant = self.service.create(
            name="CopySwift AI",
            email="admin@copyswiftai.com",
        )

        old_key = merchant["api_key"]

        updated = self.service.rotate_api_key(
            merchant["merchant_id"]
        )

        self.assertNotEqual(
            old_key,
            updated["api_key"]
        )


if __name__ == "__main__":
    unittest.main()
