import asyncio
import websockets

# Custom WebSocket handler
async def websocket_handler(websocket):
    print("Client connected")
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            # Echo the message back to the client (or add your custom logic here)
            await websocket.send(f"Echo: {message}")
    except websockets.ConnectionClosed:
        print("Client disconnected")

# Start the WebSocket server
async def start_server(ip, port):
    print("Starting WebSocket server...")
    server = await websockets.serve(websocket_handler, ip, port)
    print(f"WebSocket server started successfully on ws://{ip}:{port}")

    try:
        # Keep the server running
        await server.wait_closed()
    except asyncio.CancelledError:
        print("WebSocket server is shutting down...")
    finally:
        print("WebSocket server closed.")

# Run the server
if __name__ == "__main__":
    ip = "localhost"  # Replace with your desired IP
    port = 8765       # Replace with your desired port

    try:
        asyncio.get_event_loop().run_until_complete(start_server(ip, port))
    except KeyboardInterrupt:
        print("Server stopped by user")