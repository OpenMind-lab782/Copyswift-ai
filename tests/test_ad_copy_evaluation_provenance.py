import os
import unittest
from unittest.mock import patch

from app import app, _ad_copy_evaluation_provenance


class TestAdCopyEvaluationProvenance(unittest.TestCase):
    def test_provenance_is_server_side_and_non_sensitive(self):
        evaluation = {
            "items": [
                {"content": "private campaign text", "score": {"overall": 82, "evaluation_source": "ai"}},
                {"content": "another private campaign", "score": {"overall": 74, "evaluation_source": "heuristic"}},
            ]
        }

        with app.test_request_context(
            headers={
                "Rndr-Id": "request-123",
                "CF-Ray": "ray-456",
            }
        ), patch.dict(
            os.environ,
            {
                "RENDER_GIT_COMMIT": "commit-789",
                "RENDER_INSTANCE_ID": "instance-012",
            },
            clear=False,
        ):
            provenance = _ad_copy_evaluation_provenance(evaluation)

        self.assertEqual(provenance["request_id"], "request-123")
        self.assertEqual(provenance["edge_request_id"], "ray-456")
        self.assertEqual(provenance["deployment_commit"], "commit-789")
        self.assertEqual(provenance["deployment_instance"], "instance-012")
        self.assertEqual(provenance["evaluator"], "EvaluationEngine")
        self.assertEqual(provenance["policy"], "bounded-score-0-100-v1")
        self.assertEqual(provenance["sources"], ["ai", "heuristic"])
        self.assertNotIn("private campaign text", str(provenance))
        self.assertNotIn("another private campaign", str(provenance))


if __name__ == "__main__":
    unittest.main()
