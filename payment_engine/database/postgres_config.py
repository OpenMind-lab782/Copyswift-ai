import os


class PostgreSQLConfig:

    @staticmethod
    def database_url():
        return os.getenv(
            "DATABASE_URL",
            "postgresql://user:password@localhost:5432/swift_payment"
        )

    @staticmethod
    def is_configured():
        return "DATABASE_URL" in os.environ
