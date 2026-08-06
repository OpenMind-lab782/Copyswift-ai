from tests.base import SwiftEngineTestCase
from payment_engine.repositories import payment_repository


class RepositoryTests(SwiftEngineTestCase):

    def test_repository_instance_exists(self):
        self.assertIsNotNone(payment_repository)

    def test_repository_has_required_methods(self):
        self.assertTrue(hasattr(payment_repository, "save"))
        self.assertTrue(hasattr(payment_repository, "get"))
        self.assertTrue(hasattr(payment_repository, "list"))
        self.assertTrue(hasattr(payment_repository, "update_status"))


if __name__ == "__main__":
    import unittest
    unittest.main()
