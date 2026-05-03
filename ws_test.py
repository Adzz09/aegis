import asyncio
import websockets

async def hello():
    async with websockets.connect('ws://localhost:8000/ws/state') as ws:
        print(await ws.recv())

asyncio.run(hello())
