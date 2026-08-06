import unittest

from payment_engine.retry import RetryPolicy


class TestRetryPolicy(unittest.TestCase):

    def test_success_without_retry(self):
        retry = RetryPolicy(retries=3)

        result = retry.execute(lambda: "OK")

        self.assertEqual(result, "OK")

    def test_retry_until_success(self):
        retry = RetryPolicy(retries=3)

        attempts = {"count": 0}

        def work():
            attempts["count"] += 1

            if attempts["count"] < 3:
                raise RuntimeError("temporary")

            return "DONE"

        result = retry.execute(work)

        self.assertEqual(result, "DONE")
        self.assertEqual(attempts["count"], 3)

    def test_retry_failure(self):
        retry = RetryPolicy(retries=2)

        with self.assertRaises(RuntimeError):
            retry.execute(
                lambda: (_ for _ in ()).throw(RuntimeError("failed"))
            )


if __name__ == "__main__":
    unittest.main()
