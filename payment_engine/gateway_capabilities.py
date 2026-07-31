from dataclasses import dataclass


@dataclass(frozen=True)
class GatewayCapabilities:
    supports_cards: bool = False
    supports_bank_transfer: bool = False
    supports_mobile_money: bool = False
    supports_crypto: bool = False
    supports_refunds: bool = False
