import asyncio
import websockets

async def main():
    async with websockets.connect("wss://api.derivws.com/trading/v1/options/ws/public") as ws:
        print("CONNECTED: True")
        print("READY:", await ws.recv())

asyncio.run(main())
