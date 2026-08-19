"""
CopySwiftAI™ Ecosystem Product Registry.

Provides a lightweight registry for ecosystem products without
coupling product implementations to the kernel.
"""


class ProductRegistry:
    """Registers and resolves CopySwiftAI™ ecosystem products."""

    def __init__(self):
        self._products = {}

    def register(self, name, product=None):
        if product is None:
            product = {}

        self._products[name] = product

    def get(self, name):
        return self._products.get(name)

    def list_products(self):
        return sorted(self._products.keys())

    def exists(self, name):
        return name in self._products
