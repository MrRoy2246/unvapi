import asyncio
import websockets

async def test_connection():
    uri = "ws://127.0.0.1:8080"
    async with websockets.connect(uri) as websocket:
        print("Connection established!")
        await websocket.send("Hello Server")
        response = await websocket.recv()
        print(f"Received: {response}")

# Run the client
asyncio.run(test_connection())
