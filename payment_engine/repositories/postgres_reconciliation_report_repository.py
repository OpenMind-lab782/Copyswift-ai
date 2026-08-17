from sqlalchemy import text

from payment_engine.database.postgres import PostgreSQLDatabase


class PostgreSQLReconciliationReportRepository:
    """
    PostgreSQL-backed reconciliation report repository.

    Repository construction never provisions schema.
    """

    def __init__(self, database=None):
        self.db = database or PostgreSQLDatabase()

    def save(self, merchant_id, record):
        statement = text(
            """
            INSERT INTO reconciliation_report_records (
                merchant_id,
                reference,
                amount,
                currency
            )
            VALUES (
                :merchant_id,
                :reference,
                :amount,
                :currency
            )
            """
        )

        parameters = {
            "merchant_id": merchant_id,
            "reference": record.get("reference"),
            "amount": record.get("amount"),
            "currency": record.get("currency"),
        }

        with self.db.engine.begin() as connection:
            connection.execute(statement, parameters)

        return record

    def list(self, merchant_id):
        statement = text(
            """
            SELECT
                reference,
                amount,
                currency
            FROM reconciliation_report_records
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
            DELETE FROM reconciliation_report_records
            """
        )

        with self.db.engine.begin() as connection:
            connection.execute(statement)
