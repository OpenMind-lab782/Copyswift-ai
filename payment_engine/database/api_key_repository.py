from payment_engine.database.database import SessionLocal
from payment_engine.database.api_key_model import APIKey


class APIKeyRepository:

    def create(self, application, api_key):
        session = SessionLocal()

        try:
            record = APIKey(
                application=application,
                api_key=api_key,
                active=True
            )

            session.add(record)
            session.commit()

            return record

        finally:
            session.close()

    def get_by_key(self, api_key):
        session = SessionLocal()

        try:
            return (
                session.query(APIKey)
                .filter(APIKey.api_key == api_key)
                .first()
            )

        finally:
            session.close()

    def revoke(self, api_key):
        session = SessionLocal()

        try:
            record = (
                session.query(APIKey)
                .filter(APIKey.api_key == api_key)
                .first()
            )

            if not record:
                return False

            record.active = False

            session.commit()

            return True

        finally:
            session.close()
