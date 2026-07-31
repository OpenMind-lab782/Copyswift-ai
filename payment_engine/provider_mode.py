from enum import Enum


class ProviderMode(str, Enum):
    MOCK = "mock"
    SANDBOX = "sandbox"
    LIVE = "live"


class ProviderModeManager:
    """
    Controls the operating mode for payment providers.
    """

    def __init__(self, default_mode=ProviderMode.MOCK):
        self._mode = default_mode

    @property
    def mode(self):
        return self._mode

    def set_mode(self, mode):
        if isinstance(mode, str):
            mode = ProviderMode(mode.lower())

        self._mode = mode

    def is_mock(self):
        return self._mode == ProviderMode.MOCK

    def is_sandbox(self):
        return self._mode == ProviderMode.SANDBOX

    def is_live(self):
        return self._mode == ProviderMode.LIVE
