import json

from payment_engine.database.sqlite import db


class SQLitePaymentEventRepository:

    def __init__(self, database=None):
        self.db = database or db

    def save(self, reference, event, connection=None):
        owns_connection = connection is None
        connection = connection or self.db.connection
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO payment_events (
                reference,
                event,
                status,
                timestamp,
                metadata
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                reference,
                event.get("event"),
                event.get("status"),
                event.get("timestamp"),
                json.dumps(event.get("metadata", {})),
            ),
        )

        if owns_connection:
            self.db.commit()

        return event

    def has_verified_event(self, reference):
        cursor = self.db.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM payment_events
            WHERE reference = ?
              AND event = ?
              AND status = ?
            LIMIT 1
            """,
            (reference, "verified", "verified"),
        )

        return cursor.fetchone() is not None

    def list(self, reference):
        cursor = self.db.cursor()

        cursor.execute(
            """
            SELECT
                event,
                status,
                timestamp,
                metadata
            FROM payment_events
            WHERE reference = ?
            ORDER BY id ASC
            """,
            (reference,),
        )

        events = []

        for row in cursor.fetchall():
            event = dict(row)

            try:
                event["metadata"] = json.loads(
                    event.get("metadata") or "{}"
                )
            except Exception:
                event["metadata"] = {}

            events.append(event)

        return events

    def clear(self):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM payment_events")
        self.db.commit()
