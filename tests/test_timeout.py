import time
import unittest

from payment_engine.timeout import TimeoutPolicy, TimeoutError


class TestTimeoutPolicy(unittest.TestCase):

    def test_operation_within_timeout(self):
        policy = TimeoutPolicy(timeout=1.0)

        result = policy.execute(lambda: "OK")

        self.assertEqual(result, "OK")

    def test_operation_timeout(self):
        policy = TimeoutPolicy(timeout=0.05)

        def slow():
            time.sleep(0.10)
            return "DONE"

        with self.assertRaises(TimeoutError):
            policy.execute(slow)


if __name__ == "__main__":
    unittest.main()
