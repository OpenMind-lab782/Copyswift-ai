from tests.base import SwiftEngineTestCase
from payment_engine.config import settings


class SettingsTests(SwiftEngineTestCase):

    def test_environment_exists(self):
        self.assertIsNotNone(settings.environment)

    def test_database_exists(self):
        self.assertTrue(settings.database.endswith(".db"))

    def test_gateway_mode_exists(self):
        self.assertIn(
            settings.gateway_mode,
            ["mock", "sandbox", "live"]
        )


if __name__ == "__main__":
    import unittest
    unittest.main()
