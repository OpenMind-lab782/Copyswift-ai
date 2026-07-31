import unittest

from payment_engine.database.sqlite import db


class SQLiteCleanupTests(unittest.TestCase):

    def test_database_has_close_method(self):
        self.assertTrue(callable(db.close))


if __name__ == "__main__":
    unittest.main()
