class Middleware:
    """Base middleware interface."""

    def before(self, operation, context):
        return context

    def after(self, operation, context, result):
        return result


class MiddlewareManager:
    def __init__(self):
        self._middleware = []

    def add(self, middleware):
        self._middleware.append(middleware)

    def before(self, operation, context):
        for middleware in self._middleware:
            context = middleware.before(operation, context)
        return context

    def after(self, operation, context, result):
        for middleware in self._middleware:
            result = middleware.after(operation, context, result)
        return result

    def clear(self):
        self._middleware.clear()
