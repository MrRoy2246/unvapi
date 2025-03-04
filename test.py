import asyncio
import websockets
import json
import hmac
import hashlib
import base64
import time
import random
from urllib.parse import urlparse, parse_qs

class WebSocketHandler:
    SECRET = "123456"
    LAPI_REGISTER = "/LAPI/V1.0/System/UpServer/Register"
    LAPI_KEEPALIVE = "/LAPI/V1.0/System/UpServer/Keepalive"
    LAPI_UNREGISTER = "/LAPI/V1.0/System/UpServer/Unregister"

    def __init__(self):
        self.handshaker = None

    async def handle_connection(self, websocket, path):
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        finally:
            print(f"Client disconnected: {websocket.remote_address}")

    async def handle_message(self, websocket, message):
        if isinstance(message, str):
            await self.handle_text_message(websocket, message)
        elif isinstance(message, bytes):
            await self.handle_binary_message(websocket, message)

    async def handle_text_message(self, websocket, message):
        try:
            data = json.loads(message)
            request_url = data.get('requestURL')

            if request_url == self.LAPI_KEEPALIVE:
                print(f"Received keep-alive request from {websocket.remote_address}")
                # Handle keep-alive logic here
            elif request_url == self.LAPI_UNREGISTER:
                print(f"Device disconnected: {websocket.remote_address}")
                await websocket.close()
            else:
                print(f"Received unknown request: {request_url}")
        except json.JSONDecodeError:
            print("Invalid JSON received")

    async def handle_binary_message(self, websocket, message):
        print("Binary messages are not supported")

    @staticmethod
    def get_cnonce():
        return str(int(random.random() * time.time()))

    @staticmethod
    def generate_signature(data):
        key = WebSocketHandler.SECRET.encode('utf-8')
        message = data.encode('utf-8')
        signature = hmac.new(key, message, hashlib.sha256).digest()
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def parse_query_string(query_string):
        return {k: v[0] for k, v in parse_qs(query_string).items()}

async def main():
    handler = WebSocketHandler()
    server = await websockets.serve(
        handler.handle_connection,
        "localhost",
        8080
    )
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
