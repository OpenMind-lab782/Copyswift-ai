import unittest

from payment_engine.repositories.postgres_payment_repository import (
    PostgreSQLPaymentRepository,
)


class PostgreSQLRepositoryTests(unittest.TestCase):

    def setUp(self):
        self.repository = PostgreSQLPaymentRepository()

    def test_repository_exists(self):
        self.assertIsNotNone(self.repository)

    def test_methods_raise_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.repository.list()


if __name__ == "__main__":
    unittest.main()
