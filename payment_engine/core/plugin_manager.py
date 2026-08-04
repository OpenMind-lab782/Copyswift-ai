"""
AI Plugin Manager
"""


class PluginManager:
    """
    Registers and manages AI plugins.
    """

    def __init__(self):
        self._plugins = {}

    def register(self, name, plugin):
        self._plugins[name] = plugin

    def get(self, name):
        return self._plugins.get(name)

    def list_plugins(self):
        return sorted(self._plugins.keys())

    def exists(self, name):
        return name in self._plugins
