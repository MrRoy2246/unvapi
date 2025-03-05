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

# Constants
SECRET = "123456"
LAPI_REGISTER = "/LAPI/V1.0/System/UpServer/Register"
LAPI_KEEPALIVE = "/LAPI/V1.0/System/UpServer/Keepalive"
LAPI_UNREGISTER = "/LAPI/V1.0/System/UpServer/Unregister"

executor = ThreadPoolExecutor(max_workers=3)  # Thread pool for keep-alive tasks

def getCnonce():
    """Generates a unique client nonce (Cnonce)."""
    return str(int(random.random() * time.time()))

async def handle_websocket(websocket):
    """Handles WebSocket connections."""
    print(f"Device connected: {websocket.remote_address}")

    try:
        async for message in websocket:
            print(f"Received message: {message}")  # Debugging: Log the full message
            
            try:
                # Attempt to parse JSON
                data = json.loads(message)
                request_url = data.get("requestURL")

                if not request_url:
                    print("Error: requestURL is missing or None")
                    continue  # Skip this iteration and wait for a valid message

                # Handle keep-alive messages
                if request_url == LAPI_KEEPALIVE:
                    print(f"Keep-alive received from {websocket.remote_address}")
                    executor.submit(keep_alive_task, websocket, data)

                # Handle registration messages
                elif request_url.startswith(LAPI_REGISTER + "?Vendor"):
                    print(f"Handling registration from {websocket.remote_address}")
                    await handle_registration(websocket, request_url)

                # Handle unregistration messages
                elif request_url == LAPI_UNREGISTER:
                    print(f"Device {websocket.remote_address} unregistered")
                    await websocket.close()

                else:
                    print(f"Unknown request: {request_url}")

            except json.JSONDecodeError:
                print("Error: Received invalid JSON")

            except Exception as e:
                print(f"Unexpected error while processing message: {e}")

    except websockets.exceptions.ConnectionClosedError:
        print(f"Device {websocket.remote_address} disconnected unexpectedly")

    except Exception as e:
        print(f"Unexpected error in WebSocket handler: {e}")

    finally:
        print(f"Device disconnected: {websocket.remote_address}")
async def handle_registration(websocket, request_url):
    """Handles device registration."""
    parsed_url = urllib.parse.urlparse(request_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

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
    print(f"Certified Signature: {decoded_url}")

    pstr = f"{Vendor}/{DeviceType}/{DeviceCode}/{Algorithm}/{Nonce}"
    sha256_HMAC = hmac.new(SECRET.encode("utf-8"), pstr.encode("utf-8"), hashlib.sha256)
    encodeStr = base64.b64encode(sha256_HMAC.digest()).decode("utf-8")

    if not hmac.compare_digest(encodeStr, decoded_url):
        print(f"Authentication failed: {encodeStr}")
        await websocket.send(json.dumps({"Nonce": getCnonce()}))
        return

    print("Authentication successful")
    await websocket.send(json.dumps({"Cnonce": Cnonce, "Resign": encodeStr}))

def keep_alive_task(websocket, jsonObject):
    """Handles keep-alive requests in a separate thread."""
    try:
        print(f"Processing Keep-Alive from {websocket.remote_address}: {jsonObject}")
        time.sleep(2)
        print(f"Keep-Alive processing complete for {websocket.remote_address}")
    except Exception as e:
        print(f"Error during keep-alive processing: {e}")

async def websocket_server(ip, port):
    """Starts the WebSocket server."""
    print(f"WebSocket Server running on ws://{ip}:{port}")
    async with websockets.serve(handle_websocket, ip, port):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(websocket_server("0.0.0.0", 8765))
