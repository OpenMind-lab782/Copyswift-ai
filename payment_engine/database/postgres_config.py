import os


class PostgreSQLConfig:
    """
    Central PostgreSQL configuration.

    SQLAlchemy explicitly uses the psycopg 3 driver through the
    postgresql+psycopg:// URL scheme.

    The default URL remains suitable for deployment configuration,
    while local Termux development continues to use SQLite unless
    PostgreSQL is explicitly selected.
    """

    @staticmethod
    def database_url():
        return os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://user:password@localhost:5432/swift_payment",
        )

    @staticmethod
    def is_configured():
        return "DATABASE_URL" in os.environ
