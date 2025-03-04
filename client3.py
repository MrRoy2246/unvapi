import asyncio
import websockets

async def connect():
    uri = "ws://localhost:9090"  # WebSocket URL
    async with websockets.connect(uri) as websocket:
        print("Connected to server!")
        try:
            response = await websocket.recv()
            print(f"Received from server: {response}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(connect())
