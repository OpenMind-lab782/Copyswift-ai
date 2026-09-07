import os
import tempfile
import unittest


class CreditAbuseProtectionTests(unittest.TestCase):
    def test_failed_document_export_does_not_charge(self):
        import importlib.util
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            os.chdir(tmp)
            try:
                spec = importlib.util.spec_from_file_location("app_failure_test", os.path.join(old_cwd, "app.py"))
                app = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(app)
                app.app.config["TESTING"] = True
                email = "doc-failure@example.com"
                app.add_credits(email, 60)
                client = app.app.test_client()
                client.get("/")
                ctx = client.session_transaction()
                session = ctx.__enter__()
                session["user_email"] = email
                ctx.__exit__(None, None, None)
                original = app.document_kernel.document_studio.export_document
                app.document_kernel.document_studio.export_document = lambda document, output_name=None: (_ for _ in ()).throw(RuntimeError("forced export failure"))
                try:
                    response = client.post("/document-studio/export", json={"document": {"type": "document"}})
                finally:
                    app.document_kernel.document_studio.export_document = original
                self.assertEqual(response.status_code, 500)
                self.assertEqual(app.get_credit_balance(email), 60)
            finally:
                os.chdir(old_cwd)

    def test_successful_document_export_charges_60(self):
        import importlib.util
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            os.chdir(tmp)
            try:
                spec = importlib.util.spec_from_file_location("app_success_test", os.path.join(old_cwd, "app.py"))
                app = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(app)
                app.app.config["TESTING"] = True
                email = "doc-success@example.com"
                app.add_credits(email, 60)
                client = app.app.test_client()
                client.get("/")
                ctx = client.session_transaction()
                session = ctx.__enter__()
                session["user_email"] = email
                ctx.__exit__(None, None, None)
                original = app.document_kernel.document_studio.export_document
                app.document_kernel.document_studio.export_document = lambda document, output_name=None: b"%PDF-test"
                try:
                    response = client.post("/document-studio/export", json={"document": {"type": "document"}})
                finally:
                    app.document_kernel.document_studio.export_document = original
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.mimetype, "application/pdf")
                self.assertEqual(app.get_credit_balance(email), 0)
            finally:
                os.chdir(old_cwd)

    def test_document_export_requires_60_credits(self):
        import importlib.util
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            os.chdir(tmp)
            try:
                spec = importlib.util.spec_from_file_location("app_credit_gate_test", os.path.join(old_cwd, "app.py"))
                app = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(app)
                app.app.config["TESTING"] = True
                email = "doc-gate@example.com"
                app.add_credits(email, 59)
                client = app.app.test_client()
                client.get("/")
                ctx = client.session_transaction()
                session = ctx.__enter__()
                session["user_email"] = email
                ctx.__exit__(None, None, None)
                response = client.post("/document-studio/export", json={"document": {}})
                self.assertEqual(response.status_code, 402)
                self.assertEqual(app.get_credit_balance(email), 59)
            finally:
                os.chdir(old_cwd)

    def test_document_export_requires_login(self):
        import importlib.util
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            os.chdir(tmp)
            try:
                spec = importlib.util.spec_from_file_location("app_auth_test", os.path.join(old_cwd, "app.py"))
                app = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(app)
                app.app.config["TESTING"] = True
                client = app.app.test_client()
                response = client.post("/document-studio/export", json={"document": {}})
                self.assertEqual(response.status_code, 401)
            finally:
                os.chdir(old_cwd)

    def test_atomic_credit_deduction(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            os.chdir(tmp)
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("app_credit_test", os.path.join(old_cwd, "app.py"))
                app = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(app)
                email = "credit-test@example.com"
                app.add_credits(email, 59)
                self.assertFalse(app.deduct_credit(email, 60))
                self.assertEqual(app.get_credit_balance(email), 59)
                app.add_credits(email, 1)
                self.assertTrue(app.deduct_credit(email, 60))
                self.assertEqual(app.get_credit_balance(email), 0)
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
