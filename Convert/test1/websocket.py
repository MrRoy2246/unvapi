import asyncio
import websockets
import logging

# Custom handler for WebSocket communication
async def handler(websocket, path):
    try:
        # Handle WebSocket messages here, you can interact with the websocket
        print(f"Connection established: {websocket.remote_address}")
        while True:
            message = await websocket.recv()  # Receive a message from the client
            print(f"Message received: {message}")
            # Send a response to the client
            await websocket.send(f"Echo: {message}")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        print(f"Connection closed: {websocket.remote_address}")

# Function to start the WebSocket server
async def start_server(ip, port):
    # Start the server on the given IP and port
    async with websockets.serve(handler, ip, port):
        print(f"WebSocket server started on {ip}:{port}")
        await asyncio.Future()  # Keeps the server running indefinitely

# Main entry point
if __name__ == "__main__":
    ip = "localhost"  # IP address (can be changed)
    port = 8080  # Port (can be changed)

    try:
        # Run the WebSocket server
        asyncio.run(start_server(ip, port))
    except Exception as e:
        print(f"Failed to start server: {e}")
