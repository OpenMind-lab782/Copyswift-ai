import asyncio
import json
import websockets

async def main():
    async with websockets.connect("wss://api.derivws.com/trading/v1/options/ws/public") as ws:
        await ws.send(json.dumps({"ticks": "R_100", "subscribe": 1, "req_id": 1}))
        print("CONNECTED: True")
        for _ in range(5):
            response = json.loads(await ws.recv())
            print("TICK:", response)

asyncio.run(main())
