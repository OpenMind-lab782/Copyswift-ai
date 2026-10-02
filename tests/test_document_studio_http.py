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

    def test_save_requires_login(self):
        public = self.repository.create({"name": "test.pdf", "pages": []}, b"%PDF-save-login%", "u@example.com")
        response = self.client.post("/document-studio/save", json={"document_token": public["document_token"], "document": {"pages": []}, "expected_revision": 0})
        self.assertEqual(response.status_code, 401)

    def test_save_persists_current_document_and_advances_revision(self):
        baseline = {"name": "test.pdf", "pages": [{"number": 1, "width": 300, "height": 300, "elements": [{"id": "text-1", "type": "text", "content": "Before", "x": 10, "y": 20, "width": 100, "height": 20}]}]}
        public = self.repository.create(baseline, b"%PDF-save-http%", "u@example.com")
        with self.client.session_transaction() as session:
            session["user_email"] = "u@example.com"
        proposed = {"pages": [{"number": 1, "width": 300, "height": 300, "elements": [{"id": "text-1", "type": "text", "content": "After", "x": 30, "y": 40, "width": 100, "height": 20}]}]}
        response = self.client.post("/document-studio/save", json={"document_token": public["document_token"], "document": proposed, "expected_revision": 0})
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["document_token"], public["document_token"])
        self.assertEqual(body["revision"], 1)
        self.assertEqual(body["document"]["pages"][0]["elements"][0]["content"], "After")
        stored = self.repository.get(public["document_token"], "u@example.com")
        self.assertEqual(stored["revision"], 1)
        self.assertEqual(stored["document"]["pages"][0]["elements"][0]["content"], "After")

    def test_reopen_returns_server_saved_document_and_revision(self):
        baseline = {
            "name": "test.pdf",
            "page_count": 1,
            "pages": [{
                "number": 1,
                "width": 300,
                "height": 300,
                "elements": [{
                    "id": "text-1",
                    "type": "text",
                    "content": "Saved",
                    "x": 30,
                    "y": 40,
                    "width": 100,
                    "height": 20,
                }],
            }],
        }
        public = self.repository.create(
            baseline,
            b"%PDF-reopen-http%",
            "u@example.com",
        )

        with self.client.session_transaction() as session:
            session["user_email"] = "u@example.com"

        response = self.client.post(
            "/document-studio/reopen",
            json={"document_token": public["document_token"]},
        )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["document_token"], public["document_token"])
        self.assertEqual(body["revision"], 0)
        expected_document = dict(baseline)
        expected_document["original_sha256"] = public["original_sha256"]
        self.assertEqual(body["document"], expected_document)
        self.assertNotIn("original_bytes", body["document"])

    def test_save_rejects_wrong_owner(self):
        public = self.repository.create({"name": "test.pdf", "pages": []}, b"%PDF-save-owner%", "u@example.com")
        with self.client.session_transaction() as session:
            session["user_email"] = "other@example.com"
        response = self.client.post("/document-studio/save", json={"document_token": public["document_token"], "document": {"pages": []}, "expected_revision": 0})
        self.assertEqual(response.status_code, 404)

    def test_save_rejects_stale_revision(self):
        baseline = {"name": "test.pdf", "pages": [{"number": 1, "width": 300, "height": 300, "elements": [{"id": "text-1", "type": "text", "content": "Before", "x": 10, "y": 20, "width": 100, "height": 20}]}]}
        public = self.repository.create(baseline, b"%PDF-save-stale-http%", "u@example.com")
        with self.client.session_transaction() as session:
            session["user_email"] = "u@example.com"
        first = {"pages": [{"number": 1, "width": 300, "height": 300, "elements": [{"id": "text-1", "type": "text", "content": "First", "x": 10, "y": 20, "width": 100, "height": 20}]}]}
        response = self.client.post("/document-studio/save", json={"document_token": public["document_token"], "document": first, "expected_revision": 0})
        self.assertEqual(response.status_code, 200)
        stale = {"pages": [{"number": 1, "width": 300, "height": 300, "elements": [{"id": "text-1", "type": "text", "content": "Stale", "x": 10, "y": 20, "width": 100, "height": 20}]}]}
        response = self.client.post("/document-studio/save", json={"document_token": public["document_token"], "document": stale, "expected_revision": 0})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.get_json()["error"], "Document Studio workspace revision conflict.")
        stored = self.repository.get(public["document_token"], "u@example.com")
        self.assertEqual(stored["revision"], 1)
        self.assertEqual(stored["document"]["pages"][0]["elements"][0]["content"], "First")

    def test_save_rejects_server_owned_document_fields(self):
        public = self.repository.create({"name": "test.pdf", "pages": []}, b"%PDF-save-owned-http%", "u@example.com")
        with self.client.session_transaction() as session:
            session["user_email"] = "u@example.com"
        response = self.client.post("/document-studio/save", json={"document_token": public["document_token"], "document": {"document_token": "attacker-token", "pages": []}, "expected_revision": 0})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Document Studio save rejected.")

    def test_save_rejects_invalid_revision(self):
        public = self.repository.create({"name": "test.pdf", "pages": []}, b"%PDF-save-revision-http%", "u@example.com")
        with self.client.session_transaction() as session:
            session["user_email"] = "u@example.com"
        response = self.client.post("/document-studio/save", json={"document_token": public["document_token"], "document": {"pages": []}, "expected_revision": True})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "A non-negative document revision is required.")

    def test_export_uses_server_stored_original_bytes(self):
        original = b'%PDF-server-original%'
        public = self.repository.create({'name': 'test.pdf', 'page_count': 1, 'pages': []}, original, 'u@example.com')
        client_document = {'name': 'test.pdf', 'page_count': 1, 'pages': [], 'original_bytes': 'ATTACKER-CONTROLLED-BYTES', 'original_sha256': 'attacker'}
        with self.client.session_transaction() as session:
            session['user_email'] = 'u@example.com'
        with patch.object(app_module, 'deduct_credits', return_value=True), patch.object(app_module.document_kernel.document_studio, 'export_document', return_value=b'%PDF-output%') as export_mock:
            response = self.client.post('/document-studio/export', json={'document_token': public['document_token'], 'expected_revision': 0, 'document': client_document})
        self.assertEqual(response.status_code, 200)
        exported_document = export_mock.call_args.args[0]
        self.assertEqual(exported_document['original_bytes'], original)
        self.assertEqual(exported_document['original_sha256'], hashlib.sha256(original).hexdigest())

    def test_export_uses_server_current_document_and_server_baseline(self):
        original = b"%PDF-server-current%"
        server_baseline = {
            "name": "test.pdf",
            "page_count": 1,
            "pages": [{
                "number": 1,
                "width": 300,
                "height": 300,
                "elements": [{
                    "id": "server-text",
                    "type": "text",
                    "content": "Server baseline",
                    "x": 10,
                    "y": 20,
                    "width": 100,
                    "height": 20,
                }],
            }],
        }
        public = self.repository.create(server_baseline, original, "u@example.com")
        saved_document = {
            "pages": [{
                "number": 1,
                "width": 300,
                "height": 300,
                "elements": [{
                    "id": "server-text",
                    "type": "text",
                    "content": "Server saved edit",
                    "x": 30,
                    "y": 40,
                    "width": 100,
                    "height": 20,
                }],
            }],
        }
        with self.client.session_transaction() as session:
            session["user_email"] = "u@example.com"
        save_response = self.client.post(
            "/document-studio/save",
            json={
                "document_token": public["document_token"],
                "document": saved_document,
                "expected_revision": 0,
            },
        )
        self.assertEqual(save_response.status_code, 200)
        self.assertEqual(save_response.get_json()["revision"], 1)

        malicious_document = {
            "pages": [{
                "number": 1,
                "width": 999,
                "height": 999,
                "elements": [{
                    "id": "attacker-text",
                    "type": "text",
                    "content": "Attacker export state",
                    "x": 1,
                    "y": 2,
                    "width": 50,
                    "height": 10,
                }],
            }],
            "original_pages": [{
                "number": 1,
                "width": 999,
                "height": 999,
                "elements": [{
                    "id": "attacker-baseline",
                    "type": "text",
                    "content": "Attacker baseline",
                    "x": 1,
                    "y": 2,
                    "width": 50,
                    "height": 10,
                }],
            }],
            "original_bytes": "ATTACKER-CONTROLLED-BYTES",
            "original_sha256": "attacker",
        }
        with patch.object(app_module, "deduct_credits", return_value=True), patch.object(
            app_module.document_kernel.document_studio,
            "export_document",
            return_value=b"%PDF-output%",
        ) as export_mock:
            response = self.client.post(
                "/document-studio/export",
                json={
                    "document_token": public["document_token"],
                    "expected_revision": 1,
                    "document": malicious_document,
                },
            )
        self.assertEqual(response.status_code, 200)
        exported_document = export_mock.call_args.args[0]
        self.assertEqual(exported_document["pages"], saved_document["pages"])
        self.assertEqual(exported_document["original_pages"], server_baseline["pages"])
        self.assertEqual(exported_document["original_bytes"], original)
        self.assertEqual(
            exported_document["original_sha256"],
            hashlib.sha256(original).hexdigest(),
        )

    def test_export_rejects_stale_revision(self):
        baseline = {"name": "test.pdf", "page_count": 1, "pages": [{"number": 1, "width": 300, "height": 300, "elements": [{"id": "server-text", "type": "text", "content": "Before", "x": 10, "y": 20, "width": 100, "height": 20}]}]}
        public = self.repository.create(baseline, b"%PDF-export-stale%", "u@example.com")
        saved_document = {"pages": [{"number": 1, "width": 300, "height": 300, "elements": [{"id": "server-text", "type": "text", "content": "After", "x": 30, "y": 40, "width": 100, "height": 20}]}]}
        with self.client.session_transaction() as session:
            session["user_email"] = "u@example.com"
        save_response = self.client.post("/document-studio/save", json={"document_token": public["document_token"], "document": saved_document, "expected_revision": 0})
        self.assertEqual(save_response.status_code, 200)
        self.assertEqual(save_response.get_json()["revision"], 1)
        with patch.object(app_module.document_kernel.document_studio, "export_document") as export_mock:
            response = self.client.post("/document-studio/export", json={"document_token": public["document_token"], "expected_revision": 0})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.get_json()["error"], "Document Studio workspace revision conflict.")
        export_mock.assert_not_called()

    def test_export_requires_login(self):
        original = b'%PDF-login-required%'
        public = self.repository.create({'name': 'test.pdf', 'page_count': 1, 'pages': []}, original, 'u@example.com')
        response = self.client.post('/document-studio/export', json={'document_token': public['document_token'], 'expected_revision': 0})
        self.assertEqual(response.status_code, 401)

    def test_export_rejects_wrong_owner(self):
        original = b'%PDF-owner%'
        public = self.repository.create({'name': 'test.pdf', 'page_count': 1, 'pages': []}, original, 'u@example.com')
        with self.client.session_transaction() as session:
            session['user_email'] = 'other@example.com'
        response = self.client.post('/document-studio/export', json={'document_token': public['document_token'], 'expected_revision': 0})
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
            response = self.client.post('/document-studio/export', json={'document_token': public['document_token'], 'expected_revision': 0})
        self.assertEqual(response.status_code, 402)
        deduct_mock.assert_called_once_with('u@example.com', 60)


    def test_export_deducts_exactly_60_credits(self):
        original = b'%PDF-credit-deduction%'
        public = self.repository.create({'name': 'test.pdf', 'page_count': 1, 'pages': []}, original, 'u@example.com')
        with self.client.session_transaction() as session:
            session['user_email'] = 'u@example.com'
        with patch.object(app_module, 'deduct_credits', return_value=True) as deduct_mock, patch.object(app_module.document_kernel.document_studio, 'export_document', return_value=b'%PDF-output%'):
            response = self.client.post('/document-studio/export', json={'document_token': public['document_token'], 'expected_revision': 0})
        self.assertEqual(response.status_code, 200)
        deduct_mock.assert_called_once_with('u@example.com', 60)


    def test_frontend_export_payload_includes_top_level_document_token(self):
        html = open('templates/document_studio.html').read()
        self.assertIn('JSON.stringify({document_token:documentData.document_token,expected_revision:documentData.revision})', html)

    def test_admin_export_bypasses_credit_deduction(self):
        original = b'%PDF-admin%'
        public = self.repository.create({'name': 'test.pdf', 'page_count': 1, 'pages': []}, original, 'u@example.com')
        with self.client.session_transaction() as session:
            session.clear(); session['admin_logged_in'] = True
        self.assertIsNotNone(self.repository.get(public['document_token'], None))
        with patch.object(app_module, 'deduct_credits') as deduct_mock, patch.object(app_module.document_kernel.document_studio, 'export_document', return_value=b'%PDF-output%'):
            response = self.client.post('/document-studio/export', json={'document_token': public['document_token'], 'expected_revision': 0})
        self.assertEqual(response.status_code, 200)
        deduct_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
