from sqlalchemy import text

from payment_engine.database.postgres import PostgreSQLDatabase


class PostgreSQLSettlementRepository:
    """
    PostgreSQL-backed settlement repository.

    Schema provisioning is intentionally external to repository
    construction. Deployment/bootstrap code owns schema creation.
    """

    def __init__(self, database=None):
        self.db = database or PostgreSQLDatabase()

    def save(self, merchant_id, settlement):
        statement = text(
            """
            INSERT INTO settlements (
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
            "reference": settlement.get("reference"),
            "amount": settlement.get("amount"),
            "currency": settlement.get("currency"),
        }

        with self.db.engine.begin() as connection:
            connection.execute(statement, parameters)

        return settlement

    def list(self, merchant_id):
        statement = text(
            """
            SELECT
                merchant_id,
                reference,
                amount,
                currency
            FROM settlements
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
            DELETE FROM settlements
            """
        )

        with self.db.engine.begin() as connection:
            connection.execute(statement)
