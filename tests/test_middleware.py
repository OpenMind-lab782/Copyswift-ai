import unittest

from payment_engine.middleware import Middleware, MiddlewareManager


class RecordingMiddleware(Middleware):
    def __init__(self):
        self.calls = []

    def before(self, operation, context):
        self.calls.append(("before", operation))
        context["before"] = True
        return context

    def after(self, operation, context, result):
        self.calls.append(("after", operation))
        if isinstance(result, dict):
            result["after"] = True
        return result


class TestMiddlewareManager(unittest.TestCase):

    def test_before_and_after(self):
        manager = MiddlewareManager()
        middleware = RecordingMiddleware()

        manager.add(middleware)

        context = manager.before(
            "verify_payment",
            {}
        )

        result = manager.after(
            "verify_payment",
            context,
            {}
        )

        self.assertTrue(context["before"])
        self.assertTrue(result["after"])
        self.assertEqual(
            middleware.calls,
            [
                ("before", "verify_payment"),
                ("after", "verify_payment"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
