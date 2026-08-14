import unittest

from sqlalchemy import create_engine

from payment_engine.database.postgres import PostgreSQLDatabase


class PostgreSQLDatabaseAdapterTests(unittest.TestCase):

    def test_adapter_can_be_constructed_with_injected_engine(self):
        engine = create_engine(
            "sqlite:///:memory:",
            future=True,
        )

        database = PostgreSQLDatabase(
            database_url="sqlite:///:memory:",
            engine=engine,
        )

        self.assertIs(database.engine, engine)

        database.dispose()

    def test_health_check_uses_engine(self):
        engine = create_engine(
            "sqlite:///:memory:",
            future=True,
        )

        database = PostgreSQLDatabase(
            database_url="sqlite:///:memory:",
            engine=engine,
        )

        self.assertTrue(database.health_check())

        database.dispose()

    def test_execute_supports_parameterized_sql(self):
        engine = create_engine(
            "sqlite:///:memory:",
            future=True,
        )

        database = PostgreSQLDatabase(
            database_url="sqlite:///:memory:",
            engine=engine,
        )

        database.execute(
            "CREATE TABLE test_table (value INTEGER)"
        )

        database.execute(
            "INSERT INTO test_table (value) VALUES (:value)",
            {"value": 71},
        )

        with database.connect() as connection:
            result = connection.execute(
                __import__("sqlalchemy").text(
                    "SELECT value FROM test_table"
                )
            ).scalar_one()

        self.assertEqual(result, 71)

        database.dispose()


if __name__ == "__main__":
    unittest.main()
