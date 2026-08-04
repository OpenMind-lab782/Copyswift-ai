"""
Knowledge Loader
"""

import json
from pathlib import Path


class KnowledgeLoader:
    """
    Loads CopySwiftAI knowledge from disk.
    """

    def __init__(self, filename="knowledge/copyswiftai.json"):
        self.path = Path(filename)
        self._cache = None

    def load(self):
        if self._cache is None:
            with self.path.open("r", encoding="utf-8") as f:
                self._cache = json.load(f)
        return self._cache

    def platform(self):
        return self.load().get("platform", {})

    def plans(self):
        return self.load().get("plans", {})

    def features(self):
        return self.load().get("features", [])
