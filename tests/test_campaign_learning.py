import os
import tempfile
import unittest

import app
from brain.campaign_learning import persist_learning


class CampaignLearningSchemaTests(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(delete=False)
        self.db_file.close()
        self.original_db_path = app.DB_PATH
        app.DB_PATH = self.db_file.name
        app.init_db()

    def tearDown(self):
        app.DB_PATH = self.original_db_path
        try:
            os.unlink(self.db_file.name)
        except FileNotFoundError:
            pass

    def test_init_db_guarantees_business_brain_columns(self):
        expected = {
            "brand_voice",
            "brand_style",
            "brand_goal",
            "brand_keywords",
            "brand_cta",
            "winning_headlines",
            "winning_ctas",
            "customer_objections",
            "marketing_notes",
            "seasonal_campaigns",
            "last_campaign_summary",
        }
        with app.get_db() as db:
            columns = {row["name"] for row in db.execute("PRAGMA table_info(business_profiles)")}
        self.assertTrue(expected.issubset(columns))

    def test_persist_learning_requires_validation_and_persists_high_score(self):
        with app.get_db() as db:
            db.execute(
                "INSERT INTO business_profiles (email, business_name, product, audience) VALUES (?,?,?,?)",
                ("learn@example.com", "Learning Test", "Test Product", "Test Audience"),
            )
            profile_id = db.execute("SELECT id FROM business_profiles WHERE email=?", ("learn@example.com",)).fetchone()[0]
            db.commit()

            self.assertFalse(
                persist_learning(db, profile_id, "Unsupported campaign", {"overall": 100}, validated=False)
            )
            row = db.execute("SELECT last_campaign_summary, marketing_notes FROM business_profiles WHERE id=?", (profile_id,)).fetchone()
            self.assertIsNone(row["last_campaign_summary"])
            self.assertIsNone(row["marketing_notes"])

            self.assertTrue(
                persist_learning(db, profile_id, "Validated campaign copy", {"overall": 90}, validated=True)
            )
            db.commit()
            row = db.execute("SELECT last_campaign_summary, marketing_notes FROM business_profiles WHERE id=?", (profile_id,)).fetchone()

        self.assertEqual(row["last_campaign_summary"], "Validated campaign copy")
        self.assertIn("High-performing campaign (Score: 90)", row["marketing_notes"])


if __name__ == "__main__":
    unittest.main()
