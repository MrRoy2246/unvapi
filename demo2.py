import asyncio
import base64
import hmac
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web, WSMsgType
from urllib.parse import unquote, parse_qs

# Configuration matching Java constants
SECRET = "123456"
LAPI_REGISTER = "/LAPI/V1.0/System/UpServer/Register"
LAPI_KEEPALIVE = "/LAPI/V1.0/System/UpServer/Keepalive"
LAPI_UNREGISTER = "/LAPI/V1.0/System/UpServer/Unregister"
CORE_POOL_SIZE = 50
MAX_POOL_SIZE = 100
QUEUE_SIZE = 1000
KEEP_ALIVE_TIME = 60  # Seconds

# Thread pool matching Java's ThreadPoolExecutor
executor = ThreadPoolExecutor(
    max_workers=MAX_POOL_SIZE,
    thread_name_prefix="KeepLiveThreadPool"
)

async def handle_http(request):
    """Handles HTTP registration requests"""
    path = request.path
    remote = request.remote
    print(f"HTTP request from {remote}: {path}")

    if path == LAPI_REGISTER:
        return await handle_registration(request)
    
    return web.Response(status=404, text="Not Found")

async def handle_registration(request):
    """Implements Java's handleHttpRequest logic"""
    params = parse_qs(request.query_string)
    response = web.Response(content_type="application/json")
    
    # First registration attempt (no parameters)
    if not params:
        response.status = 401
        response.text = json.dumps({"Nonce": get_cnonce()})
        return response
    
    # Second registration with parameters
    try:
        vendor = params["Vendor"][0]
        device_type = params["DeviceType"][0]
        device_code = params["DeviceCode"][0]
        algorithm = params["Algorithm"][0]
        nonce = params["Nonce"][0]
        sign = unquote(params["Sign"][0]).replace(" ", "+")

        # Validate signature (matches Java's logic)
        message = f"{vendor}/{device_type}/{device_code}/{algorithm}/{nonce}"
        secret = SECRET.encode("utf-8")
        mac = hmac.new(secret, message.encode("utf-8"), hashlib.sha256)
        expected_sign = base64.b64encode(mac.digest()).decode()
        
        if expected_sign != sign:
            raise ValueError("Invalid signature")

        # Successful authentication
        response.text = json.dumps({
            "Cnonce": get_cnonce(),
            "Resign": expected_sign
        })
        return response

    except (KeyError, ValueError) as e:
        print(f"Authentication failed: {str(e)}")
        response.status = 401
        response.text = json.dumps({"Nonce": get_cnonce()})
        return response

async def websocket_handler(request):
    """Implements WebSocketHandler logic from Java code"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    remote = request.remote
    print(f"WebSocket connected: {remote}")

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                
                # Handle keep-alive requests (matches KeepLiveThread)
                if data.get("RequestURL") == LAPI_KEEPALIVE:
                    executor.submit(
                        handle_keepalive,
                        ws,
                        data,
                        remote
                    )
                
                # Handle unregister requests
                elif data.get("RequestURL") == LAPI_UNREGISTER:
                    await ws.close()
    
    finally:
        print(f"Connection closed: {remote}")
        await ws.close()

def handle_keepalive(ws, data, remote):
    """Matches KeepLiveThread.run() functionality"""
    try:
        # Create response (matches Java's KeepAliveRspAO)
        response = {
            "ResponseURL": LAPI_KEEPALIVE,
            "ResponseCode": 0,  # SUCCESS
            "ResponseString": "Success",
            "Cseq": data.get("Cseq"),
            "Data": {
                "Timestamp": int(time.time()),
                "Timeout": KEEP_ALIVE_TIME
            }
        }
        
        # Thread-safe send
        asyncio.run_coroutine_threadsafe(
            ws.send_str(json.dumps(response)),
            asyncio.get_event_loop()
        )
        print(f"Sent keep-alive response to {remote}")

    except Exception as e:
        print(f"Error handling keep-alive: {str(e)}")

def get_cnonce():
    """Matches Java's getCnonce() implementation"""
    d = time.time()
    return str(int((time.time() % 1) * d))

app = web.Application()
app.add_routes([
    web.get(LAPI_REGISTER, handle_http),
    web.get("/ws", websocket_handler)
])

if __name__ == "__main__":
    print("Starting server...")
    web.run_app(app, host="localhost", port=82)