from contextlib import contextmanager

from payment_engine.database.sqlite import db


class TransactionManager:

    def __init__(self, database=None):
        self.database = database or db

    @contextmanager
    def transaction(self, database=None):
        database = database or self.database

        if hasattr(database, "engine"):
            with database.engine.begin() as connection:
                yield connection
            return

        database.begin()
        try:
            yield database.connection
            database.commit()
        except Exception:
            database.rollback()
            raise

    def execute(self, operation, *args, database=None, **kwargs):
        with self.transaction(database=database) as connection:
            return operation(
                *args,
                connection=connection,
                **kwargs,
            )
