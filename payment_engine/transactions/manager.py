from payment_engine.database.sqlite import db


class TransactionManager:

    def __init__(self, database=None):
        self.database = database or db

    def execute(self, operation, *args, **kwargs):

        self.database.begin()

        try:
            result = operation(*args, **kwargs)
            self.database.commit()
            return result

        except Exception:
            self.database.rollback()
            raise
