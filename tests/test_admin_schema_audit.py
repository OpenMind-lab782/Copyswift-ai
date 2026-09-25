import os
import tempfile
import unittest

import app


class AdminSchemaAuditTests(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(delete=False)
        self.db_file.close()
        self.original_db_path = app.DB_PATH
        app.DB_PATH = self.db_file.name
        app.init_db()
        self.client = app.app.test_client()

    def tearDown(self):
        app.DB_PATH = self.original_db_path
        try:
            os.unlink(self.db_file.name)
        except FileNotFoundError:
            pass

    def test_schema_audit_requires_admin(self):
        response = self.client.get("/admin/schema/credit-purchases")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])

    def test_admin_schema_audit_returns_credit_purchase_schema(self):
        with self.client.session_transaction() as session:
            session.clear()
            session["admin_logged_in"] = True

        response = self.client.get("/admin/schema/credit-purchases")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["table"], "credit_purchases")
        self.assertIsInstance(payload["table_info"], list)
        self.assertIsInstance(payload["index_list"], list)

        columns = {column["name"] for column in payload["table_info"]}
        self.assertIn("tx_ref", columns)


if __name__ == "__main__":
    unittest.main()
