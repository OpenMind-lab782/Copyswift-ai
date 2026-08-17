import json

from sqlalchemy import text

from payment_engine.database.postgres import PostgreSQLDatabase


class PostgreSQLPaymentEventRepository:

    def __init__(self, database=None):
        self.db = database or PostgreSQLDatabase()

    @staticmethod
    def _serialize_metadata(metadata):
        if metadata is None:
            return "{}"
        return json.dumps(metadata)

    @staticmethod
    def _deserialize_metadata(metadata):
        if not metadata:
            return {}

        if isinstance(metadata, dict):
            return metadata

        try:
            return json.loads(metadata)
        except (TypeError, ValueError):
            return {}

    @classmethod
    def _row_to_event(cls, row):
        if row is None:
            return None

        return {
            "id": row.get("id"),
            "reference": row.get("reference"),
            "event": row.get("event"),
            "status": row.get("status"),
            "timestamp": row.get("timestamp"),
            "metadata": cls._deserialize_metadata(
                row.get("metadata")
            ),
        }

    def save(self, reference, event, connection=None):
        statement = text(
            """
            INSERT INTO payment_events (
                reference,
                event,
                status,
                timestamp,
                metadata
            )
            VALUES (
                :reference,
                :event,
                :status,
                :timestamp,
                :metadata
            )
            """
        )

        parameters = {
            "reference": reference,
            "event": event.get("event"),
            "status": event.get("status"),
            "timestamp": event.get("timestamp"),
            "metadata": self._serialize_metadata(
                event.get("metadata", {})
            ),
        }

        if connection is not None:
            connection.execute(statement, parameters)
        else:
            with self.db.engine.begin() as connection:
                connection.execute(statement, parameters)

        return event

    def list(self, reference):
        statement = text(
            """
            SELECT
                id,
                reference,
                event,
                status,
                timestamp,
                metadata
            FROM payment_events
            WHERE reference = :reference
            ORDER BY id ASC
            """
        )

        with self.db.connect() as connection:
            rows = connection.execute(
                statement,
                {"reference": reference},
            ).mappings().all()

        return [
            self._row_to_event(row)
            for row in rows
        ]

    def clear(self):
        statement = text("DELETE FROM payment_events")

        with self.db.engine.begin() as connection:
            connection.execute(statement)
