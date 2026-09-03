import asyncio
import json
import websockets

async def main():
    async with websockets.connect("wss://ws.derivws.com/websockets/v3?app_id=1089") as ws:
        await ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        print("CONNECTED: True")
        print("TICK:", (await ws.recv())[:1000])

asyncio.run(main())
