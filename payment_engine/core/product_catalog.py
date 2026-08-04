"""
CopySwiftAI Product Catalog
"""


class ProductCatalog:

    def __init__(self):
        self._plans = {
            "starter": {
                "name": "Starter",
                "description": "Ideal for individuals and freelancers."
            },
            "pro": {
                "name": "Pro",
                "description": "Designed for growing businesses and teams."
            },
            "enterprise": {
                "name": "Enterprise",
                "description": "Advanced features for organizations."
            },
        }

    def get_plan(self, key):
        return self._plans.get(key)

    def list_plans(self):
        return dict(self._plans)
