import asyncio
import json
import websockets
from datetime import UTC, datetime
from trading.market.provider import MarketTick
from trading.strategies.momentum import MomentumStrategy

async def main():
    async with websockets.connect("wss://api.derivws.com/trading/v1/options/ws/public") as ws:
        await ws.send(json.dumps({"ticks_history": "R_100", "count": 20, "end": "latest", "style": "ticks", "req_id": 1}))
        response = json.loads(await ws.recv())
        history = response["history"]
        ticks = [MarketTick(symbol="R_100", bid=float(price), ask=float(price), timestamp=datetime.fromtimestamp(epoch, tz=UTC)) for price, epoch in zip(history["prices"], history["times"])]
        signal = MomentumStrategy(lookback=20).evaluate(ticks)
        print("HISTORICAL_TICKS:", len(ticks))
        print("SIGNAL_VALID:", signal.validate())
        print("SIGNAL:", signal)

asyncio.run(main())
