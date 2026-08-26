from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from payment_engine.database.postgres_config import PostgreSQLConfig


class PostgreSQLDatabase:
    """
    SQLAlchemy-backed PostgreSQL database adapter.

    The adapter is intentionally independent from the payment repository.
    This allows repositories and services to work with a stable database
    abstraction while the underlying PostgreSQL driver is selected by the
    deployment environment.
    """

    def __init__(self, database_url=None, engine=None):
        self.database_url = (
            database_url
            or PostgreSQLConfig.database_url()
        )

        self.engine = engine or create_engine(
            self.database_url,
            future=True,
            pool_pre_ping=True,
        )

    def connect(self):
        return self.engine.connect()

    def begin(self):
        return self.engine.begin()

    def execute(self, statement, parameters=None):
        with self.engine.begin() as connection:
            return connection.execute(
                text(statement),
                parameters or {},
            )

    def health_check(self):
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False

    def dispose(self):
        self.engine.dispose()
