import os
from datetime import UTC, datetime
import requests
from trading.market.provider import MarketDataProvider, MarketTick

class OandaMarketDataProvider(MarketDataProvider):
    def __init__(self, account_id=None, token=None, practice=True, timeout=10):
        self.account_id = account_id or os.getenv("OANDA_ACCOUNT_ID")
        self.token = token or os.getenv("OANDA_API_TOKEN")
        self.base_url = "https://api-fxpractice.oanda.com" if practice else "https://api-fxtrade.oanda.com"
        self.timeout = timeout

    def _headers(self):
        if not self.token:
            raise RuntimeError("OANDA_API_TOKEN is not configured")
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}

    def get_tick(self, symbol: str) -> MarketTick:
        if not self.account_id:
            raise RuntimeError("OANDA_ACCOUNT_ID is not configured")
        instrument = symbol.replace("/", "_").upper()
        url = f"{self.base_url}/v3/accounts/{self.account_id}/pricing"
        response = requests.get(url, headers=self._headers(), params={"instruments": instrument}, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        prices = payload.get("prices", [])
        if not prices:
            raise RuntimeError(f"No OANDA price returned for {instrument}")
        price = prices[0]
        bid = float(price["bids"][0]["price"])
        ask = float(price["asks"][0]["price"])
        timestamp = datetime.fromisoformat(price["time"].replace("Z", "+00:00")).astimezone(UTC)
        tick = MarketTick(instrument, bid, ask, timestamp)
        tick.validate()
        return tick
