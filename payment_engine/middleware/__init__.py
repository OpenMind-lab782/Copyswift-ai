class Middleware:
    """Base middleware contract for payment-engine operations."""

    def before(self, operation, context):
        return context

    def after(self, operation, context, result):
        return result


class MiddlewareManager:
    """Executes registered middleware around an operation."""

    def __init__(self):
        self._middleware = []

    def add(self, middleware):
        if not isinstance(middleware, Middleware):
            raise TypeError("middleware must be a Middleware instance")

        self._middleware.append(middleware)
        return middleware

    def before(self, operation, context):
        for middleware in self._middleware:
            context = middleware.before(operation, context)
        return context

    def after(self, operation, context, result):
        for middleware in reversed(self._middleware):
            result = middleware.after(operation, context, result)
        return result


__all__ = [
    "Middleware",
    "MiddlewareManager",
]
