from payment_engine.database.sqlite import db


class SQLitePaymentEventRepository:

    def __init__(self, database=None):
        self.db = database or db

    def save(self, reference, event):
        cursor = self.db.cursor()

        cursor.execute("""
        INSERT INTO payment_events (
            reference,
            event,
            status,
            timestamp
        )
        VALUES (?, ?, ?, ?)
        """, (
            reference,
            event.get("event"),
            event.get("status"),
            event.get("timestamp")
        ))

        self.db.commit()

        return event

    def list(self, reference):
        cursor = self.db.cursor()

        cursor.execute(
            """
            SELECT event,
                   status,
                   timestamp
            FROM payment_events
            WHERE reference = ?
            ORDER BY id ASC
            """,
            (reference,)
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def clear(self):
        cursor = self.db.cursor()

        cursor.execute(
            "DELETE FROM payment_events"
        )

        self.db.commit()
