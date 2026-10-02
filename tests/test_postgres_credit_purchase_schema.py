import unittest

from sqlalchemy import create_engine, inspect

from payment_engine.database.postgres import PostgreSQLDatabase
from payment_engine.database.postgres_schema import initialize_postgres_schema


class PostgreSQLCreditPurchaseSchemaTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            future=True,
        )
        self.database = PostgreSQLDatabase(
            database_url="sqlite:///:memory:",
            engine=self.engine,
        )
        initialize_postgres_schema(self.database)

    def tearDown(self):
        self.database.dispose()

    def test_payment_reference_is_unique(self):

        with self.engine.begin() as connection:
            connection.exec_driver_sql(
                """
                INSERT INTO credit_purchases (
                    payment_reference,
                    customer_email,
                    package,
                    credits,
                    amount,
                    currency,
                    gateway,
                    status
                ) VALUES (
                    'PAY-UNIQUE-001',
                    'customer@example.com',
                    'Starter',
                    50,
                    8,
                    'USD',
                    'paystack',
                    'pending'
                )
                """
            )

            with self.assertRaises(Exception):
                connection.exec_driver_sql(
                    """
                    INSERT INTO credit_purchases (
                        payment_reference,
                        customer_email,
                        package,
                        credits,
                        amount,
                        currency,
                        gateway,
                        status
                    ) VALUES (
                        'PAY-UNIQUE-001',
                        'customer@example.com',
                        'Starter',
                        50,
                        8,
                        'USD',
                        'paystack',
                        'pending'
                    )
                    """
                )

    def test_credit_purchases_table_exists_with_required_columns(self):
        inspector = inspect(self.engine)
        self.assertIn("credit_purchases", inspector.get_table_names())

        columns = {
            column["name"]
            for column in inspector.get_columns("credit_purchases")
        }

        self.assertEqual(
            columns,
            {
                "id",
                "payment_reference",
                "customer_email",
                "package",
                "credits",
                "amount",
                "currency",
                "gateway",
                "status",
                "ref_code",
                "created_at",
                "activated_at",
            },
        )


if __name__ == "__main__":
    unittest.main()
