import hashlib
import unittest
from sqlalchemy import create_engine, text
from payment_engine.database.postgres import PostgreSQLDatabase
from ecosystem_core.document_studio_workspace import DocumentStudioWorkspaceRepository

class DocumentStudioWorkspaceRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", future=True)
        self.database = PostgreSQLDatabase(database_url="sqlite:///:memory:", engine=self.engine)
        DocumentStudioWorkspaceRepository.initialize_schema(self.database)
        self.repository = DocumentStudioWorkspaceRepository(database=self.database)

    def tearDown(self):
        self.database.dispose()

    def test_create_get_and_owner_isolation(self):
        original = b"%PDF-original%"
        public = self.repository.create({"name": "x.pdf", "pages": []}, original, "u@example.com")
        self.assertIn("document_token", public)
        self.assertNotIn("original_bytes", public)
        stored = self.repository.get(public["document_token"], "u@example.com")
        self.assertEqual(stored["original_bytes"], original)
        self.assertEqual(stored["original_sha256"], hashlib.sha256(original).hexdigest())
        self.assertIsNone(self.repository.get(public["document_token"], "other@example.com"))

    def test_tampered_original_is_rejected(self):
        original = b"%PDF-original%"
        public = self.repository.create({"name": "x.pdf", "pages": []}, original, "u@example.com")
        with self.engine.begin() as connection:
            connection.execute(text("UPDATE document_studio_workspaces SET original_bytes = :data"), {"data": b"%PDF-tampered%"})
        with self.assertRaisesRegex(ValueError, "integrity verification"):
            self.repository.get(public["document_token"], "u@example.com")

if __name__ == "__main__":
    unittest.main()
