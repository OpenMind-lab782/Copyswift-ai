from payment_engine.provider_mode import ProviderMode


class GatewayConfig:
    """
    Stores per-gateway configuration.
    """

    def __init__(self):
        self._config = {}

    def configure(self, gateway_name, mode=ProviderMode.MOCK):
        if isinstance(mode, str):
            mode = ProviderMode(mode.lower())

        self._config[gateway_name] = {
            "mode": mode
        }

    def get(self, gateway_name):
        return self._config.get(
            gateway_name,
            {"mode": ProviderMode.MOCK},
        )

    def mode(self, gateway_name):
        return self.get(gateway_name)["mode"]

    def all(self):
        return dict(self._config)
