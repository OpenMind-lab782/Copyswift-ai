import asyncio
import json
import websockets

async def main():
    async with websockets.connect("wss://api.derivws.com/trading/v1/options/ws/public") as ws:
        await ws.send(json.dumps({"active_symbols": "brief", "req_id": 1}))
        print("CONNECTED: True")
        response = json.loads(await ws.recv())
        print("RESPONSE:", response)

asyncio.run(main())
