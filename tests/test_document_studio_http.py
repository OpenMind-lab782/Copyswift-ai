import unittest
import hashlib
from io import BytesIO
from unittest.mock import patch

from sqlalchemy import create_engine

from app import app
import app as app_module
from ecosystem_core.document_studio_workspace import DocumentStudioWorkspaceRepository
from payment_engine.database.postgres import PostgreSQLDatabase


class DocumentStudioHttpTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.engine = create_engine("sqlite:///:memory:", future=True)
        self.database = PostgreSQLDatabase(
            database_url="sqlite:///:memory:",
            engine=self.engine,
        )
        DocumentStudioWorkspaceRepository.initialize_schema(self.database)
        self.repository = DocumentStudioWorkspaceRepository(database=self.database)
        self.previous_repository = app_module._document_studio_workspace_repository
        app_module._document_studio_workspace_repository = self.repository

    def tearDown(self):
        app_module._document_studio_workspace_repository = self.previous_repository
        self.database.dispose()

    def test_identity_sets_user_email_session(self):
        response = self.client.post("/document-studio/identity", json={"email": " U@Example.COM "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"user_email": "u@example.com"})
        with self.client.session_transaction() as session:
            self.assertEqual(session.get("user_email"), "u@example.com")

    def test_identity_rejects_missing_email(self):
        response = self.client.post("/document-studio/identity", json={"email": ""})
        self.assertEqual(response.status_code, 400)
        with self.client.session_transaction() as session:
            self.assertIsNone(session.get("user_email"))

    def test_identity_then_import_binds_workspace_to_session_email(self):
        identity = self.client.post("/document-studio/identity", json={"email": "owner@example.com"})
        self.assertEqual(identity.status_code, 200)
        original = b"%PDF-identity-http-boundary%"
        parsed = {"name": "test.pdf", "page_count": 1, "pages": [], "original_bytes": original}
        with patch.object(app_module.document_kernel.document_studio, "import_binary_document", return_value=parsed):
            response = self.client.post("/document-studio/import", data={"file": (BytesIO(original), "test.pdf")}, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 200)
        token = response.get_json()["document_token"]
        stored = self.repository.get(token, "owner@example.com")
        self.assertIsNotNone(stored)
        self.assertEqual(stored["original_bytes"], original)

    def test_export_uses_server_stored_original(self):
        original = b'%PDF-server-original%'
        public = self.repository.create({'name': 'test.pdf', 'page_count': 1, 'pages': []}, original, 'u@example.com')
        client_document = {'name': 'test.pdf', 'page_count': 1, 'pages': [], 'original_bytes': 'ATTACKER-CONTROLLED-BYTES', 'original_sha256': 'attacker'}
        with self.client.session_transaction() as session:
            session['user_email'] = 'u@example.com'
        with patch.object(app_module, 'deduct_credits', return_value=True), patch.object(app_module.document_kernel.document_studio, 'export_document', return_value=b'%PDF-output%') as export_mock:
            response = self.client.post('/document-studio/export', json={'document_token': public['document_token'], 'document': client_document})
        self.assertEqual(response.status_code, 200)
        exported_document = export_mock.call_args.args[0]
        self.assertEqual(exported_document['original_bytes'], original)
        self.assertEqual(exported_document['original_sha256'], hashlib.sha256(original).hexdigest())

    def test_export_requires_login(self):
        original = b'%PDF-login-required%'
        public = self.repository.create({'name': 'test.pdf', 'page_count': 1, 'pages': []}, original, 'u@example.com')
        response = self.client.post('/document-studio/export', json={'document_token': public['document_token'], 'document': {'name': 'test.pdf', 'pages': []}})
        self.assertEqual(response.status_code, 401)

    def test_export_rejects_wrong_owner(self):
        original = b'%PDF-owner%'
        public = self.repository.create({'name': 'test.pdf', 'page_count': 1, 'pages': []}, original, 'u@example.com')
        with self.client.session_transaction() as session:
            session['user_email'] = 'other@example.com'
        response = self.client.post('/document-studio/export', json={'document_token': public['document_token'], 'document': {'name': 'test.pdf', 'pages': []}})
        self.assertEqual(response.status_code, 404)

    def test_import_returns_public_document_without_original_bytes(self):
        original = b"%PDF-http-boundary%"
        parsed = {
            "name": "test.pdf",
            "page_count": 1,
            "pages": [],
            "original_bytes": original,
            "original_sha256": "ignored",
            "metadata": {"source_format": "pdf"},
        }

        with patch.object(
            app_module.document_kernel.document_studio,
            "import_binary_document",
            return_value=parsed,
        ):
            response = self.client.post(
                "/document-studio/import",
                data={"file": (BytesIO(original), "test.pdf")},
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

        body = response.get_json()
        self.assertIn("document_token", body)
        self.assertNotIn("original_bytes", body)
        self.assertEqual(
            body["original_sha256"],
            hashlib.sha256(original).hexdigest(),
        )


    def test_export_requires_60_credits(self):
        original = b'%PDF-credit-gate%'
        public = self.repository.create({'name': 'test.pdf', 'page_count': 1, 'pages': []}, original, 'u@example.com')
        with self.client.session_transaction() as session:
            session['user_email'] = 'u@example.com'
        with patch.object(app_module, 'deduct_credits', return_value=False) as deduct_mock, patch.object(app_module.document_kernel.document_studio, 'export_document', return_value=b'%PDF-output%'):
            response = self.client.post('/document-studio/export', json={'document_token': public['document_token'], 'document': {'name': 'test.pdf', 'pages': []}})
        self.assertEqual(response.status_code, 402)
        deduct_mock.assert_called_once_with('u@example.com', 60)


    def test_export_deducts_exactly_60_credits(self):
        original = b'%PDF-credit-deduction%'
        public = self.repository.create({'name': 'test.pdf', 'page_count': 1, 'pages': []}, original, 'u@example.com')
        with self.client.session_transaction() as session:
            session['user_email'] = 'u@example.com'
        with patch.object(app_module, 'deduct_credits', return_value=True) as deduct_mock, patch.object(app_module.document_kernel.document_studio, 'export_document', return_value=b'%PDF-output%'):
            response = self.client.post('/document-studio/export', json={'document_token': public['document_token'], 'document': {'name': 'test.pdf', 'pages': []}})
        self.assertEqual(response.status_code, 200)
        deduct_mock.assert_called_once_with('u@example.com', 60)


    def test_frontend_export_payload_includes_top_level_document_token(self):
        html = open('templates/document_studio.html').read()
        self.assertIn('JSON.stringify({document_token:documentData.document_token,document:documentData})', html)

    def test_admin_export_bypasses_credit_deduction(self):
        original = b'%PDF-admin%'
        public = self.repository.create({'name': 'test.pdf', 'page_count': 1, 'pages': []}, original, 'u@example.com')
        with self.client.session_transaction() as session:
            session.clear(); session['admin_logged_in'] = True
        self.assertIsNotNone(self.repository.get(public['document_token'], None))
        with patch.object(app_module, 'deduct_credits') as deduct_mock, patch.object(app_module.document_kernel.document_studio, 'export_document', return_value=b'%PDF-output%'):
            response = self.client.post('/document-studio/export', json={'document_token': public['document_token'], 'document': {'name': 'test.pdf', 'pages': []}})
        self.assertEqual(response.status_code, 200)
        deduct_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
