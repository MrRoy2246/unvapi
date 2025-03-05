import asyncio
import base64
import hmac
import hashlib
import json
import math
import time
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web, WSMsgType

# Constants and Configurations
SECRET = "123456"
LAPI_REGISTER = "/LAPI/V1.0/System/UpServer/Register"
LAPI_KEEPALIVE = "/LAPI/V1.0/System/UpServer/Keepalive"
LAPI_UNREGISTER = "/LAPI/V1.0/System/UpServer/Unregister"
KEEP_ALIVE_INTERVAL = 60

# Thread Pool Configuration
CORE_POOL_SIZE = 50
MAX_POOL_SIZE = 100
executor = ThreadPoolExecutor(max_workers=MAX_POOL_SIZE)

# Enums
class CodeEnum(Enum):
    SUCCESS = (200, "Success.", "响应成功")
    # ... other codes ...

class WebsocketCodeEnum(Enum):
    SUCCESS = (0, "Succeed")
    # ... other codes ...

# Data Classes
@dataclass
class KeepAliveRspAO:
    timestamp: int
    timeout: int

@dataclass
class WebsocketReq:
    RequestURL: str
    Method: str
    Cseq: int
    Data: dict

@dataclass
class WebsocketRsp:
    ResponseURL: str
    ResponseCode: int
    ResponseString: str
    Cseq: int
    Data: KeepAliveRspAO

# Helper Functions
def get_cnonce():
    d = time.time()
    return str(math.floor((time.time() % 1) * d))

def validate_signature(vendor, device_type, device_code, algorithm, nonce, received_sign):
    message = f"{vendor}/{device_type}/{device_code}/{algorithm}/{nonce}".encode()
    secret = SECRET.encode()
    signature = base64.b64encode(hmac.new(secret, message, hashlib.sha256).digest()).decode()
    return signature == received_sign

# WebSocket Handler
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    remote_addr = request.remote
    print(f"Connection from {remote_addr}")

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            data = json.loads(msg.data)
            req = WebsocketReq(**data)
            
            if req.RequestURL == LAPI_KEEPALIVE:
                print(f"Keep-alive received from {remote_addr}")
                response = WebsocketRsp(
                    ResponseURL=req.RequestURL,
                    ResponseCode=WebsocketCodeEnum.SUCCESS.value[0],
                    ResponseString=WebsocketCodeEnum.SUCCESS.value[1],
                    Cseq=req.Cseq,
                    Data=KeepAliveRspAO(
                        timestamp=int(time.time()),
                        timeout=KEEP_ALIVE_INTERVAL
                    )
                )
                await ws.send_str(json.dumps(response.__dict__))
                
            elif req.RequestURL == LAPI_UNREGISTER:
                print(f"Unregister request from {remote_addr}")
                await ws.close()
                
        elif msg.type == WSMsgType.ERROR:
            print(f"WebSocket error: {ws.exception()}")

    print(f"Connection closed with {remote_addr}")
    return ws

# HTTP Handler for WebSocket Upgrade
async def http_handler(request):
    path = request.path
    print(f"Handshake request for {path} from {request.remote}")

    if path == LAPI_REGISTER:
        # Handle registration logic
        return web.Response(text=json.dumps({"Nonce": get_cnonce()}), status=401)
    
    elif path.startswith(LAPI_REGISTER):
        params = request.query
        # Validate parameters and signature
        if validate_signature(params.get("Vendor"), params.get("DeviceType"),
                            params.get("DeviceCode"), params.get("Algorithm"),
                            params.get("Nonce"), params.get("Sign")):
            # Create WebSocket connection
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            return ws
        else:
            return web.Response(text=json.dumps({"Nonce": get_cnonce()}), status=401)

    return web.Response(status=404)

# Server Setup
app = web.Application()
app.add_routes([
    web.get(LAPI_REGISTER, http_handler),
    web.get("/ws", websocket_handler)
])

if __name__ == "__main__":
    web.run_app(app, host='localhost', port=82)



