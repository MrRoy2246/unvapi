import asyncio
import websockets
import json
import hmac
import hashlib
import base64
import time
import random
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

class WebSocketHandler:
    SECRET = "123456"
    LAPI_REGISTER = "/LAPI/V1.0/System/UpServer/Register"
    LAPI_KEEPALIVE = "/LAPI/V1.0/System/UpServer/Keepalive"
    LAPI_UNREGISTER = "/LAPI/V1.0/System/UpServer/Unregister"

    def __init__(self):
        self.keep_alive_executor = ThreadPoolExecutor(max_workers=3)

    async def channelRead(self, websocket, path):
        try:
            print(f"New connection from {websocket.remote_address}")
            
            if not path:
                print(f"Invalid WebSocket request: Missing path from {websocket.remote_address}")
                await websocket.close(code=4001, reason="Invalid request path")
                return

            parsed_url = urllib.parse.urlparse(path)
            valid_paths = [self.LAPI_REGISTER, self.LAPI_KEEPALIVE, self.LAPI_UNREGISTER]
            
            if parsed_url.path not in valid_paths:
                print(f"Invalid path {parsed_url.path} from {websocket.remote_address}")
                await websocket.close(code=4002, reason="Invalid path")
                return
            
            if parsed_url.path == self.LAPI_REGISTER:
                await self.handle_http_register(websocket)
            elif parsed_url.path.startswith(self.LAPI_REGISTER):
                query_params = urllib.parse.parse_qs(parsed_url.query)
                await self.handle_http_register_vendor(websocket, query_params)
            else:
                async for message in websocket:
                    await self.handleWebSocketRequest(websocket, message)
        
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed abruptly: {e}")
        except Exception as e:
            self.exceptionCaught(websocket, e)
        finally:
            self.handlerRemoved(websocket)

    async def handle_http_register(self, websocket):
        response_body = json.dumps({"Nonce": self.getCnonce()})
        await websocket.send(response_body)
        print(f"Sent initial registration challenge to {websocket.remote_address}")

    async def handle_http_register_vendor(self, websocket, query_params):
        try:
            Vendor = query_params.get("Vendor", [None])[0]
            DeviceType = query_params.get("DeviceType", [None])[0]
            DeviceCode = query_params.get("DeviceCode", [None])[0]
            Algorithm = query_params.get("Algorithm", [None])[0]
            Nonce = query_params.get("Nonce", [None])[0]
            Cnonce = query_params.get("Cnonce", [""])[0]
            Sign = query_params.get("Sign", [None])[0]

            if None in (Vendor, DeviceType, DeviceCode, Algorithm, Nonce, Sign):
                print("Missing parameters in registration request")
                await websocket.close(code=4000, reason="Missing parameters")
                return

            decoded_url = urllib.parse.unquote(Sign).replace(" ", "+")
            pstr = f"{Vendor}/{DeviceType}/{DeviceCode}/{Algorithm}/{Nonce}"

            sha256_HMAC = hmac.new(self.SECRET.encode(), pstr.encode(), hashlib.sha256)
            encodeStr = base64.b64encode(sha256_HMAC.digest()).decode()

            if not hmac.compare_digest(encodeStr, decoded_url):
                print("Authentication failed")
                await websocket.send(json.dumps({"Nonce": self.getCnonce()}))
                return

            print("Authentication successful")
            await websocket.send(json.dumps({"Cnonce": Cnonce, "Resign": encodeStr}))
            self.handlerAdded(websocket)
        except Exception as e:
            print(f"Error during vendor registration: {e}")
            await websocket.close(code=5000, reason="Internal server error")

    async def handleWebSocketRequest(self, websocket, message):
        try:
            jsonObject = json.loads(message)
            request_url = jsonObject.get("requestURL")

            if request_url == self.LAPI_KEEPALIVE:
                print(f"Received keep-alive request: {request_url}")
                asyncio.create_task(self.keep_alive_task(websocket, jsonObject))
            elif request_url == self.LAPI_UNREGISTER:
                print(f"Device {websocket.remote_address} disconnected")
                await websocket.close()
            else:
                print(f"Unknown request: {request_url}")
        except json.JSONDecodeError:
            print("Invalid JSON received")
        except Exception as e:
            self.exceptionCaught(websocket, e)

    async def keep_alive_task(self, websocket, jsonObject):
        try:
            print(f"Processing Keep-Alive from {websocket.remote_address}: {jsonObject}")
            await asyncio.sleep(2)
            print(f"Keep-Alive processing complete for {websocket.remote_address}")
        except Exception as e:
            print(f"Error during keep-alive processing {websocket.remote_address}: {e}")

    def handlerAdded(self, websocket):
        print(f"{websocket.remote_address} Device connected")
        self.channelActive(websocket)

    def handlerRemoved(self, websocket):
        print(f"{websocket.remote_address} Device removed")
        self.channelInactive(websocket)

    def channelActive(self, websocket):
        print(f"Client joined connection: {websocket.remote_address}")

    def channelInactive(self, websocket):
        print(f"Client disconnected: {websocket.remote_address}")

    def exceptionCaught(self, websocket, error):
        print(f"Exception occurred: {error}")
        asyncio.create_task(websocket.close())

    def getCnonce(self):
        return str(int(random.random() * time.time()))
    


    
async def websocket_server(ip, port):
    """
    Runs the WebSocket server.
    """
    print(f"Starting WebSocket server on {ip}:{port}...")

    async def handler(websocket, path=None):  # 🔹 Allow path to be optional
        websocket_handler = WebSocketHandler()
        await websocket_handler.channelRead(websocket, path if path else "/")  # 🔹 Ensure path is always a string

    try:
        server = await websockets.serve(handler, ip, port)  # 🔹 Ensure correct parameters
        print(f"WebSocket server started on {ip}:{port}")
        await server.wait_closed()  # 🔹 Keep the server running
    except OSError as e:
        print(f"WebSocket server failed to start: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
    finally:
        print("WebSocket Server closed.")

if __name__ == "__main__":
    IP = "localhost"
    PORT = 9090
    asyncio.run(websocket_server(IP, PORT))
