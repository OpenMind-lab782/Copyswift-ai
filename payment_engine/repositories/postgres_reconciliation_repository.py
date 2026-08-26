from sqlalchemy import text

from payment_engine.database.postgres import PostgreSQLDatabase


class PostgreSQLReconciliationRepository:
    """
    PostgreSQL-backed reconciliation repository.

    Repository construction never provisions schema.
    """

    def __init__(self, database=None):
        self.db = database or PostgreSQLDatabase()

    def save(self, merchant_id, record):
        statement = text(
            """
            INSERT INTO reconciliation_records (
                merchant_id,
                reference
            )
            VALUES (
                :merchant_id,
                :reference
            )
            """
        )

        parameters = {
            "merchant_id": merchant_id,
            "reference": record.get("reference"),
        }

        with self.db.engine.begin() as connection:
            connection.execute(statement, parameters)

        return record

    def list(self, merchant_id):
        statement = text(
            """
            SELECT
                merchant_id,
                reference
            FROM reconciliation_records
            WHERE merchant_id = :merchant_id
            ORDER BY id ASC
            """
        )

        with self.db.connect() as connection:
            rows = (
                connection.execute(
                    statement,
                    {"merchant_id": merchant_id},
                )
                .mappings()
                .all()
            )

        return [dict(row) for row in rows]

    def clear(self):
        statement = text(
            """
            DELETE FROM reconciliation_records
            """
        )

        with self.db.engine.begin() as connection:
            connection.execute(statement)
