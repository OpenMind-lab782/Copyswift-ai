import asyncio
import json
import websockets

async def main():
    async with websockets.connect("wss://api.derivws.com/trading/v1/options/ws/public") as ws:
        await ws.send(json.dumps({"ticks_history": "R_100", "count": 100, "end": "latest", "style": "ticks", "req_id": 1}))
        print("CONNECTED: True")
        response = json.loads(await ws.recv())
        print("MSG_TYPE:", response.get("msg_type"))
        print("HISTORY_COUNT:", len(response.get("history", {}).get("prices", [])))
        print("FIRST_PRICE:", response.get("history", {}).get("prices", [None])[0])
        print("LAST_PRICE:", response.get("history", {}).get("prices", [None])[-1])

asyncio.run(main())
