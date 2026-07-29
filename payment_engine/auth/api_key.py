import secrets

from payment_engine.logging.audit import AuditLogger
from payment_engine.database.api_key_repository import APIKeyRepository


class APIKeyManager:

    def __init__(self):
        self.audit = AuditLogger()
        self.repository = APIKeyRepository()

    def create_key(self, application):

        key = secrets.token_hex(32)

        self.repository.create(
            application,
            key
        )

        self.audit.log(
            action="API_KEY",
            reference=application,
            status="CREATED",
            gateway="system",
            details="Database API key generated"
        )

        return key

    def validate_key(self, key):

        record = self.repository.get_by_key(key)

        if not record:
            return False

        return record.active

    def revoke_key(self, key):

        record = self.repository.get_by_key(key)

        if not record:
            return False

        self.repository.revoke(key)

        self.audit.log(
            action="API_KEY",
            reference=record.application,
            status="REVOKED",
            gateway="system",
            details="Database API key revoked"
        )

        return True

    def get_application(self, key):

        record = self.repository.get_by_key(key)

        if not record:
            return None

        return record.application
