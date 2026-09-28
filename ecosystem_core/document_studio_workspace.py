import hashlib
import json
import secrets
import logging
from sqlalchemy import text
from payment_engine.database.postgres import PostgreSQLDatabase

logger = logging.getLogger("copyswift.document_studio.workspace")

DOCUMENT_STUDIO_WORKSPACE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS document_studio_workspaces (
    token_hash VARCHAR(64) PRIMARY KEY,
    owner_email VARCHAR(255),
    original_sha256 VARCHAR(64) NOT NULL,
    original_bytes BYTEA NOT NULL,
    baseline_document TEXT NOT NULL,
    current_document TEXT,
    revision INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


class DocumentStudioWorkspaceRepository:
    def __init__(self, database=None):
        self.db = database or PostgreSQLDatabase()

    @staticmethod
    def initialize_schema(database):
        logger.info("DS_IMPORT_WORKSPACE_SCHEMA_START")
        with database.engine.begin() as connection:
            connection.execute(text(DOCUMENT_STUDIO_WORKSPACE_SCHEMA_SQL))

            if connection.dialect.name == "sqlite":
                columns = {row["name"] for row in connection.execute(text("PRAGMA table_info(document_studio_workspaces)")).mappings()}
            else:
                columns = {row["column_name"] for row in connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = :table_name"), {"table_name": "document_studio_workspaces"}).mappings()}

            if "current_document" not in columns:
                connection.execute(text("ALTER TABLE document_studio_workspaces ADD COLUMN current_document TEXT"))

            if "revision" not in columns:
                connection.execute(text("ALTER TABLE document_studio_workspaces ADD COLUMN revision INTEGER NOT NULL DEFAULT 0"))

            connection.execute(text("UPDATE document_studio_workspaces SET current_document = baseline_document WHERE current_document IS NULL"))

        logger.info("DS_IMPORT_WORKSPACE_SCHEMA_COMPLETE")

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

    _EDITABLE_ELEMENT_KEYS = frozenset({
        "id",
        "type",
        "content",
        "x",
        "y",
        "width",
        "height",
        "font",
        "font_size",
        "color",
        "image_data",
        "image_data_base64",
        "image_format",
    })

    _SERVER_OWNED_KEYS = frozenset({
        "document_token",
        "revision",
        "owner_email",
        "created_at",
        "updated_at",
        "original_bytes",
        "original_sha256",
        "original_pages",
        "baseline_document",
        "current_document",
        "metadata",
        "page_count",
        "name",
    })

    @classmethod
    def _validate_editable_document(cls, document, baseline_document):
        if not isinstance(document, dict):
            raise TypeError("Current Document Studio state requires a dictionary.")
        if not isinstance(baseline_document, dict):
            raise TypeError("Document Studio baseline must be a dictionary.")

        forbidden = sorted(cls._SERVER_OWNED_KEYS.intersection(document))
        if forbidden:
            raise ValueError(
                "Current Document Studio state contains server-owned fields: "
                + ", ".join(forbidden)
            )

        unexpected = sorted(set(document) - {"pages"})
        if unexpected:
            raise ValueError(
                "Current Document Studio state may contain only pages; "
                "unexpected fields: " + ", ".join(unexpected)
            )

        pages = document.get("pages")
        baseline_pages = baseline_document.get("pages") or []

        if not isinstance(pages, list):
            raise TypeError("Current Document Studio pages must be a list.")
        if len(pages) != len(baseline_pages):
            raise ValueError(
                "Current Document Studio page count cannot be changed."
            )

        canonical_pages = []
        seen_ids = set()

        for page_index, (page, baseline_page) in enumerate(
            zip(pages, baseline_pages), start=1
        ):
            if not isinstance(page, dict):
                raise TypeError(
                    f"Current Document Studio page {page_index} must be a dictionary."
                )
            if not isinstance(baseline_page, dict):
                raise ValueError(
                    f"Document Studio baseline page {page_index} is invalid."
                )

            allowed_page_keys = {"number", "width", "height", "elements"}
            unexpected_page_keys = sorted(set(page) - allowed_page_keys)
            if unexpected_page_keys:
                raise ValueError(
                    f"Current Document Studio page {page_index} contains "
                    "unexpected fields: " + ", ".join(unexpected_page_keys)
                )

            for field in ("number", "width", "height"):
                if field in page and page[field] != baseline_page.get(field):
                    raise ValueError(
                        f"Current Document Studio page {page_index} "
                        f"{field} is server-authoritative."
                    )

            elements = page.get("elements")
            if not isinstance(elements, list):
                raise TypeError(
                    f"Current Document Studio page {page_index} elements must be a list."
                )

            baseline_elements = baseline_page.get("elements") or []
            baseline_by_id = {
                element.get("id"): element
                for element in baseline_elements
                if isinstance(element, dict) and element.get("id")
            }

            canonical_elements = []

            for element_index, element in enumerate(elements, start=1):
                if not isinstance(element, dict):
                    raise TypeError(
                        f"Current Document Studio element {page_index}:{element_index} "
                        "must be a dictionary."
                    )

                element_id = element.get("id")
                if not element_id:
                    raise ValueError(
                        f"Current Document Studio element {page_index}:{element_index} "
                        "requires an id."
                    )
                if element_id in seen_ids:
                    raise ValueError(
                        "Current Document Studio element ids must be unique."
                    )
                seen_ids.add(element_id)

                baseline_element = baseline_by_id.get(element_id)

                if baseline_element is not None:
                    if (
                        "type" in element
                        and element.get("type") != baseline_element.get("type")
                    ):
                        raise ValueError(
                            f"Current Document Studio element {element_id} "
                            "type is server-authoritative."
                        )

                    for key, value in element.items():
                        if key in cls._EDITABLE_ELEMENT_KEYS:
                            continue
                        if key in baseline_element and value == baseline_element[key]:
                            continue
                        raise ValueError(
                            f"Current Document Studio element {element_id} "
                            f"contains non-editable field: {key}"
                        )

                    canonical_element = dict(baseline_element)
                    for key in cls._EDITABLE_ELEMENT_KEYS:
                        if key in element:
                            canonical_element[key] = element[key]
                else:
                    unexpected_element_keys = sorted(
                        set(element) - cls._EDITABLE_ELEMENT_KEYS
                    )
                    if unexpected_element_keys:
                        raise ValueError(
                            f"New Document Studio element {element_id} contains "
                            "non-editable fields: "
                            + ", ".join(unexpected_element_keys)
                        )

                    if element.get("type") not in {"text", "image"}:
                        raise ValueError(
                            f"New Document Studio element {element_id} "
                            "must be text or image."
                        )

                    canonical_element = dict(element)

                if not canonical_element.get("type"):
                    raise ValueError(
                        f"Current Document Studio element {element_id} requires a type."
                    )

                canonical_elements.append(canonical_element)

            canonical_page = dict(baseline_page)
            canonical_page["elements"] = canonical_elements
            canonical_pages.append(canonical_page)

        return {"pages": canonical_pages}

    @staticmethod
    def _public_document(document):
        public_document = json.loads(json.dumps(document))
        public_document.pop("original_bytes", None)
        return public_document

    def create(self, document, original_bytes, owner_email=None):
        logger.info("DS_IMPORT_WORKSPACE_INSERT_START bytes=%d", len(original_bytes) if isinstance(original_bytes, (bytes, bytearray)) else -1)
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
                original_bytes, baseline_document, current_document, revision
            ) VALUES (
                :token_hash, :owner_email, :original_sha256,
                :original_bytes, :baseline_document, :current_document, 0
            )
        """)
        with self.db.engine.begin() as connection:
            connection.execute(statement, {
                "token_hash": token_hash,
                "owner_email": owner_email,
                "original_sha256": original_sha256,
                "original_bytes": original_bytes,
                "baseline_document": self._serialize_document(stored_document),
                "current_document": self._serialize_document(stored_document),
            })
            timestamps = connection.execute(
                text("SELECT created_at, updated_at FROM document_studio_workspaces WHERE token_hash = :token_hash LIMIT 1"),
                {"token_hash": token_hash},
            ).mappings().first()

        logger.info("DS_IMPORT_WORKSPACE_INSERT_COMPLETE")
        if timestamps is None:
            raise RuntimeError("Document Studio workspace timestamps could not be persisted.")
        stored_document["created_at"] = timestamps["created_at"].isoformat() if hasattr(timestamps["created_at"], "isoformat") else str(timestamps["created_at"])
        stored_document["updated_at"] = timestamps["updated_at"].isoformat() if hasattr(timestamps["updated_at"], "isoformat") else str(timestamps["updated_at"])
        public_document = self._public_document(stored_document)
        public_document["document_token"] = token
        public_document["revision"] = 0
        return public_document

    def save_current(self, token, document, expected_revision, owner_email=None):
        if not token:
            return None
        if not isinstance(document, dict):
            raise TypeError("Current Document Studio state requires a canonical document.")
        if not isinstance(expected_revision, int) or isinstance(expected_revision, bool) or expected_revision < 0:
            raise ValueError("Document Studio revision must be a non-negative integer.")

        token_hash = self._token_hash(token)
        with self.db.engine.begin() as connection:
            row = connection.execute(
                text("""
                    SELECT owner_email, original_sha256, original_bytes,
                           baseline_document, revision
                    FROM document_studio_workspaces
                    WHERE token_hash = :token_hash
                    LIMIT 1
                """),
                {"token_hash": token_hash},
            ).mappings().first()

            if row is None:
                return None
            if owner_email is not None and row["owner_email"] and row["owner_email"] != owner_email:
                return None

            original_bytes = bytes(row["original_bytes"])
            actual_sha256 = hashlib.sha256(original_bytes).hexdigest()
            if actual_sha256 != row["original_sha256"]:
                raise ValueError("Stored Document Studio original failed integrity verification.")

            baseline_document = self._deserialize_document(row["baseline_document"])
            document = self._validate_editable_document(document, baseline_document)
            serialized_document = self._serialize_document(document)

            result = connection.execute(
                text("""
                    UPDATE document_studio_workspaces
                    SET current_document = :current_document,
                        revision = revision + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE token_hash = :token_hash AND revision = :expected_revision
                """),
                {
                    "token_hash": token_hash,
                    "current_document": serialized_document,
                    "expected_revision": expected_revision,
                },
            )
            if result.rowcount != 1:
                raise ValueError("Document Studio workspace revision conflict.")

            new_revision = connection.execute(
                text("SELECT revision FROM document_studio_workspaces WHERE token_hash = :token_hash LIMIT 1"),
                {"token_hash": token_hash},
            ).scalar_one()

        return {"document": document, "revision": new_revision}

    def get(self, token, owner_email=None):
        if not token:
            return None
        statement = text("""
            SELECT token_hash, owner_email, original_sha256,
                   original_bytes, baseline_document, current_document,
                   revision, created_at, updated_at
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

        baseline_document = self._deserialize_document(row["baseline_document"])
        stored_current_document = self._deserialize_document(row["current_document"])
        if not isinstance(stored_current_document, dict):
            raise ValueError("Stored Document Studio current state is invalid.")

        current_document = self._validate_editable_document(
            {"pages": stored_current_document.get("pages") or []},
            baseline_document,
        )

        document = dict(baseline_document)
        document["pages"] = current_document["pages"]
        document["original_sha256"] = row["original_sha256"]
        document["original_bytes"] = original_bytes
        document["original_pages"] = baseline_document.get("pages") or []
        return {
            "document": document,
            "current_document": current_document,
            "baseline_document": baseline_document,
            "revision": row["revision"],
            "original_bytes": original_bytes,
            "original_sha256": row["original_sha256"],
            "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
            "updated_at": row["updated_at"].isoformat() if hasattr(row["updated_at"], "isoformat") else str(row["updated_at"]),
        }
