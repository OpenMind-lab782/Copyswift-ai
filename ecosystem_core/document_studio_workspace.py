import hashlib
import json
import secrets
from sqlalchemy import text
from payment_engine.database.postgres import PostgreSQLDatabase

DOCUMENT_STUDIO_WORKSPACE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS document_studio_workspaces (
    token_hash VARCHAR(64) PRIMARY KEY,
    owner_email VARCHAR(255),
    original_sha256 VARCHAR(64) NOT NULL,
    original_bytes BYTEA NOT NULL,
    baseline_document TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


class DocumentStudioWorkspaceRepository:
    def __init__(self, database=None):
        self.db = database or PostgreSQLDatabase()

    @staticmethod
    def initialize_schema(database):
        with database.engine.begin() as connection:
            connection.execute(text(DOCUMENT_STUDIO_WORKSPACE_SCHEMA_SQL))

    @staticmethod
    def _token_hash(token):
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _serialize_document(document):
        return json.dumps(document, separators=(",", ":"))

    @staticmethod
    def _deserialize_document(document):
        if isinstance(document, dict):
            return document
        return json.loads(document)

    @staticmethod
    def _public_document(document):
        public_document = json.loads(json.dumps(document))
        public_document.pop("original_bytes", None)
        return public_document

    def create(self, document, original_bytes, owner_email=None):
        if not isinstance(document, dict):
            raise TypeError("Document workspace requires a canonical document.")
        if not isinstance(original_bytes, (bytes, bytearray)):
            raise TypeError("Document workspace requires original PDF bytes.")

        original_bytes = bytes(original_bytes)
        original_sha256 = hashlib.sha256(original_bytes).hexdigest()
        token = secrets.token_urlsafe(32)
        token_hash = self._token_hash(token)
        stored_document = dict(document)
        stored_document["original_sha256"] = original_sha256
        stored_document.pop("original_bytes", None)

        statement = text("""
            INSERT INTO document_studio_workspaces (
                token_hash, owner_email, original_sha256,
                original_bytes, baseline_document
            ) VALUES (
                :token_hash, :owner_email, :original_sha256,
                :original_bytes, :baseline_document
            )
        """)
        with self.db.engine.begin() as connection:
            connection.execute(statement, {
                "token_hash": token_hash,
                "owner_email": owner_email,
                "original_sha256": original_sha256,
                "original_bytes": original_bytes,
                "baseline_document": self._serialize_document(stored_document),
            })

        public_document = self._public_document(stored_document)
        public_document["document_token"] = token
        return public_document

    def get(self, token, owner_email=None):
        if not token:
            return None
        statement = text("""
            SELECT token_hash, owner_email, original_sha256,
                   original_bytes, baseline_document
            FROM document_studio_workspaces
            WHERE token_hash = :token_hash
            LIMIT 1
        """)
        with self.db.connect() as connection:
            row = connection.execute(statement, {
                "token_hash": self._token_hash(token),
            }).mappings().first()

        if row is None:
            return None
        if owner_email is not None and row["owner_email"] and row["owner_email"] != owner_email:
            return None

        original_bytes = bytes(row["original_bytes"])
        actual_sha256 = hashlib.sha256(original_bytes).hexdigest()
        if actual_sha256 != row["original_sha256"]:
            raise ValueError("Stored Document Studio original failed integrity verification.")

        document = self._deserialize_document(row["baseline_document"])
        document["original_sha256"] = row["original_sha256"]
        document["original_bytes"] = original_bytes
        return {
            "document": document,
            "original_bytes": original_bytes,
            "original_sha256": row["original_sha256"],
        }
