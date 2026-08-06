class WeightedRoutingStrategy:
    """
    Selects the gateway with the highest success score.
    If multiple gateways have the same score, the first
    gateway in the candidate list is selected.
    """

    def __init__(self, metrics):
        self.metrics = metrics

    def select(self, gateways):
        if not gateways:
            return None

        best_gateway = gateways[0]
        best_score = self.metrics.get(best_gateway)["success"]

        for gateway in gateways[1:]:
            score = self.metrics.get(gateway)["success"]

            if score > best_score:
                best_gateway = gateway
                best_score = score

        return best_gateway
