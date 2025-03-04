# import asyncio
# import websockets

# async def test_client():
#     async with websockets.connect("ws://localhost:8765") as websocket:
#         await websocket.send("Hello, Server!")
#         response = await websocket.recv()
#         print(f"Received from server: {response}")

# asyncio.get_event_loop().run_until_complete(test_client())





import asyncio
import websockets

async def test_client():
    user_id = "user123"  # Example user ID
    uri = f"ws://localhost:8765/ws/{user_id}"  # Connect with dynamic path
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello, Server!")
        response = await websocket.recv()
        print(f"Received from server: {response}")

asyncio.run(test_client())
