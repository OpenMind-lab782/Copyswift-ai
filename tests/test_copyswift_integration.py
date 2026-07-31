import unittest

from payment_engine.integration import CopySwiftIntegration


class CopySwiftIntegrationTests(unittest.TestCase):

    def test_integration_exists(self):
        integration = CopySwiftIntegration()

        self.assertIsNotNone(integration)

    def test_engine_attached(self):
        integration = CopySwiftIntegration()

        self.assertIsNotNone(
            integration.engine
        )


if __name__ == "__main__":
    unittest.main()
