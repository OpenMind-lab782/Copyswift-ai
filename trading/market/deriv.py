import asyncio
import json
from datetime import UTC, datetime
import websockets
from trading.market.provider import MarketDataProvider, MarketTick

class DerivMarketDataProvider(MarketDataProvider):
    URL = "wss://api.derivws.com/trading/v1/options/ws/public"

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    async def get_tick_async(self, symbol: str) -> MarketTick:
        async with websockets.connect(self.URL, open_timeout=self.timeout) as ws:
            await ws.send(json.dumps({"ticks": symbol, "subscribe": 1, "req_id": 1}))
            response = json.loads(await asyncio.wait_for(ws.recv(), timeout=self.timeout))
            if response.get("msg_type") != "tick" or "tick" not in response:
                raise RuntimeError(f"Unexpected Deriv response: {response}")
            tick = response["tick"]
            market_tick = MarketTick(
                symbol=tick["symbol"],
                bid=float(tick["bid"]),
                ask=float(tick["ask"]),
                timestamp=datetime.fromtimestamp(tick["epoch"], tz=UTC),
            )
            market_tick.validate()
            return market_tick

    def get_tick(self, symbol: str) -> MarketTick:
        return asyncio.run(self.get_tick_async(symbol))
