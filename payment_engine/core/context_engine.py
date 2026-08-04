"""
AI Context Engine
"""


class AIContextEngine:
    """
    Stores workflow context in memory.
    """

    def __init__(self):
        self._history = []

    def add(self, workflow_result):
        self._history.append(workflow_result)

    def latest(self):
        if not self._history:
            return None
        return self._history[-1]

    def history(self):
        return list(self._history)

    def count(self):
        return len(self._history)

    def clear(self):
        self._history.clear()
