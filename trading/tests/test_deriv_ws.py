import asyncio
import json
import websockets

async def main():
    async with websockets.connect("wss://ws.derivws.com/websockets/v3?app_id=1089") as ws:
        await ws.send(json.dumps({"active_symbols": "brief", "product_type": "basic"}))
        print("CONNECTED: True")
        print("RESPONSE:", (await ws.recv())[:1000])

asyncio.run(main())
