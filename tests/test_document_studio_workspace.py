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
        self.assertIsInstance(public["created_at"], str)
        self.assertIsInstance(public["updated_at"], str)
        self.assertTrue(public["created_at"])
        self.assertTrue(public["updated_at"])
        stored = self.repository.get(public["document_token"], "u@example.com")
        self.assertEqual(stored["original_bytes"], original)
        self.assertEqual(stored["original_sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(stored["created_at"], public["created_at"])
        self.assertEqual(stored["updated_at"], public["updated_at"])
        self.assertIsNone(self.repository.get(public["document_token"], "other@example.com"))

    def test_tampered_original_is_rejected(self):
        original = b"%PDF-original%"
        public = self.repository.create({"name": "x.pdf", "pages": []}, original, "u@example.com")
        with self.engine.begin() as connection:
            connection.execute(text("UPDATE document_studio_workspaces SET original_bytes = :data"), {"data": b"%PDF-tampered%"})
        with self.assertRaisesRegex(ValueError, "integrity verification"):
            self.repository.get(public["document_token"], "u@example.com")

    def test_tampered_current_document_is_rejected(self):
        baseline = {
            "name": "x.pdf",
            "pages": [{
                "number": 1,
                "width": 300,
                "height": 300,
                "elements": [],
            }],
        }
        public = self.repository.create(
            baseline,
            b"%PDF-current-tamper%",
            "u@example.com",
        )
        tampered = {
            "pages": [{
                "number": 1,
                "width": 999,
                "height": 300,
                "elements": [],
            }],
        }
        with self.engine.begin() as connection:
            connection.execute(
                text("UPDATE document_studio_workspaces SET current_document = :current_document"),
                {"current_document": self.repository._serialize_document(tampered)},
            )
        with self.assertRaisesRegex(ValueError, "width is server-authoritative"):
            self.repository.get(public["document_token"], "u@example.com")

    def test_create_starts_revision_at_zero(self):
        public = self.repository.create(
            {"name": "x.pdf", "pages": []},
            b"%PDF-revision%",
            "u@example.com",
        )
        self.assertEqual(public["revision"], 0)
        stored = self.repository.get(public["document_token"], "u@example.com")
        self.assertEqual(stored["revision"], 0)

    def test_save_current_advances_revision_and_persists_edit(self):
        original = b"%PDF-save%"
        baseline = {
            "name": "x.pdf",
            "pages": [{
                "number": 1,
                "width": 300,
                "height": 300,
                "elements": [{
                    "id": "text-1",
                    "type": "text",
                    "content": "Before",
                    "x": 10,
                    "y": 20,
                    "width": 100,
                    "height": 20,
                }],
            }],
        }
        public = self.repository.create(baseline, original, "u@example.com")

        proposed = {
            "pages": [{
                "number": 1,
                "width": 300,
                "height": 300,
                "elements": [{
                    "id": "text-1",
                    "type": "text",
                    "content": "After",
                    "x": 30,
                    "y": 40,
                    "width": 100,
                    "height": 20,
                }],
            }],
        }

        saved = self.repository.save_current(
            public["document_token"],
            proposed,
            0,
            "u@example.com",
        )

        self.assertEqual(saved["revision"], 1)
        self.assertEqual(
            saved["document"]["pages"][0]["elements"][0]["content"],
            "After",
        )

        stored = self.repository.get(public["document_token"], "u@example.com")
        self.assertEqual(stored["revision"], 1)
        self.assertEqual(
            stored["document"]["pages"][0]["elements"][0]["content"],
            "After",
        )

    def test_save_current_image_replacement_removes_stale_base64(self):
        baseline = {
            "name": "x.pdf",
            "pages": [{
                "number": 1,
                "width": 300,
                "height": 300,
                "elements": [{
                    "id": "image-1",
                    "type": "image",
                    "x": 10,
                    "y": 20,
                    "width": 100,
                    "height": 100,
                    "image_data_base64": "OLD-IMAGE",
                    "image_format": "png",
                }],
            }],
        }
        public = self.repository.create(
            baseline,
            b"%PDF-image-replacement%",
            "u@example.com",
        )

        proposed = {
            "pages": [{
                "number": 1,
                "width": 300,
                "height": 300,
                "elements": [{
                    "id": "image-1",
                    "type": "image",
                    "x": 10,
                    "y": 20,
                    "width": 100,
                    "height": 100,
                    "image_data": "NEW-IMAGE",
                    "image_format": "png",
                }],
            }],
        }

        saved = self.repository.save_current(
            public["document_token"],
            proposed,
            0,
            "u@example.com",
        )

        saved_image = saved["document"]["pages"][0]["elements"][0]
        self.assertEqual(saved_image["image_data"], "NEW-IMAGE")
        self.assertNotIn("image_data_base64", saved_image)

        stored = self.repository.get(public["document_token"], "u@example.com")
        stored_image = stored["document"]["pages"][0]["elements"][0]
        self.assertEqual(stored_image["image_data"], "NEW-IMAGE")
        self.assertNotIn("image_data_base64", stored_image)

    def test_save_current_rejects_stale_revision(self):
        baseline = {
            "name": "x.pdf",
            "pages": [{
                "number": 1,
                "width": 300,
                "height": 300,
                "elements": [{
                    "id": "text-1",
                    "type": "text",
                    "content": "Before",
                    "x": 10,
                    "y": 20,
                    "width": 100,
                    "height": 20,
                }],
            }],
        }
        public = self.repository.create(baseline, b"%PDF-stale%", "u@example.com")

        proposed = {
            "pages": [{
                "number": 1,
                "width": 300,
                "height": 300,
                "elements": [{
                    "id": "text-1",
                    "type": "text",
                    "content": "First save",
                    "x": 10,
                    "y": 20,
                    "width": 100,
                    "height": 20,
                }],
            }],
        }

        self.repository.save_current(
            public["document_token"],
            proposed,
            0,
            "u@example.com",
        )

        stale = {
            "pages": [{
                "number": 1,
                "width": 300,
                "height": 300,
                "elements": [{
                    "id": "text-1",
                    "type": "text",
                    "content": "Stale overwrite",
                    "x": 10,
                    "y": 20,
                    "width": 100,
                    "height": 20,
                }],
            }],
        }

        with self.assertRaisesRegex(ValueError, "revision conflict"):
            self.repository.save_current(
                public["document_token"],
                stale,
                0,
                "u@example.com",
            )

        stored = self.repository.get(public["document_token"], "u@example.com")
        self.assertEqual(stored["revision"], 1)
        self.assertEqual(
            stored["document"]["pages"][0]["elements"][0]["content"],
            "First save",
        )

    def test_save_current_rejects_server_owned_fields(self):
        public = self.repository.create(
            {"name": "x.pdf", "pages": []},
            b"%PDF-owned%",
            "u@example.com",
        )
        proposed = {
            "document_token": public["document_token"],
            "pages": [],
        }

        with self.assertRaisesRegex(ValueError, "server-owned fields"):
            self.repository.save_current(
                public["document_token"],
                proposed,
                0,
                "u@example.com",
            )

    def test_save_current_keeps_baseline_page_metadata_server_authoritative(self):
        baseline = {
            "name": "x.pdf",
            "pages": [{
                "number": 1,
                "width": 300,
                "height": 300,
                "elements": [],
            }],
        }
        public = self.repository.create(
            baseline,
            b"%PDF-metadata%",
            "u@example.com",
        )

        proposed = {
            "pages": [{
                "number": 99,
                "width": 999,
                "height": 999,
                "elements": [],
            }],
        }

        with self.assertRaisesRegex(ValueError, "server-authoritative"):
            self.repository.save_current(
                public["document_token"],
                proposed,
                0,
                "u@example.com",
            )

if __name__ == "__main__":
    unittest.main()
