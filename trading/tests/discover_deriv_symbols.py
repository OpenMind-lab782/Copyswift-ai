import asyncio
import json
import websockets

async def main():
    async with websockets.connect("wss://ws.derivws.com/websockets/v3?app_id=1089") as ws:
        await ws.send(json.dumps({"active_symbols": "full", "product_type": "basic", "req_id": 1}))
        response = json.loads(await ws.recv())
        print("RAW_RESPONSE:", response)
        print("MSG_TYPE:", response.get("msg_type"))
        print("ERROR:", response.get("error"))
        symbols = response.get("active_symbols", [])
        print("SYMBOL_COUNT:", len(symbols))
        for item in symbols[:20]:
            print(item.get("symbol"), "|", item.get("display_name"), "|", item.get("market"))

asyncio.run(main())
