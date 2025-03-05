import asyncio
import base64
import hmac
import hashlib
import json
import time
from aiohttp import web, WSMsgType
from urllib.parse import unquote, parse_qs

SECRET = "123456"
REGISTER_PATH = "/LAPI/V1.0/System/UpServer/Register"
KEEP_ALIVE_INTERVAL = 10

# In-memory storage for nonces (use proper DB in production)
registrations = {}

async def handle_http(request):
    path = request.path
    remote_ip = "request.remote"
    print(f"HTTP request from {remote_ip}: {path}")

    if path == REGISTER_PATH:
        return await handle_registration(request)
    
    return web.Response(status=404, text="Not Found")

async def handle_registration(request):
    remote_ip = request.remote
    params = parse_qs(request.query_string)
    
    # First registration attempt (no parameters)
    if not any(params):
        nonce = str(int(time.time()))
        registrations[remote_ip] = {"nonce": nonce}
        return web.Response(
            status=401,
            content_type="application/json",
            text=json.dumps({"Nonce": nonce})
        )
    
    # Second registration with parameters
    try:
        vendor = params["Vendor"][0]
        device_type = params["DeviceType"][0]
        device_code = params["DeviceCode"][0]
        algorithm = params["Algorithm"][0]
        client_nonce = params["Nonce"][0]
        received_sign = unquote(params["Sign"][0]).replace(" ", "+")
        
        # Validate client nonce
        if registrations.get(remote_ip, {}).get("nonce") != client_nonce:
            return web.Response(status=401, text="Invalid nonce")
        
        # Generate server signature
        message = f"{vendor}/{device_type}/{device_code}/{algorithm}/{client_nonce}"
        signature = hmac.new(
            SECRET.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).digest()
        server_sign = base64.b64encode(signature).decode()
        print(server_sign)
        
        if server_sign != received_sign:
            return web.Response(status=401, text="Invalid signature")
        
        # Store successful registration
        registrations[remote_ip]["registered"] = True
        registrations[remote_ip]["cnonce"] = str(int(time.time()))
        
        return web.Response(
            content_type="application/json",
            text=json.dumps({
                "Cnonce": registrations[remote_ip]["cnonce"],
                "Resign": server_sign
            })
        )
        
    except KeyError as e:
        return web.Response(
            status=400,
            text=f"Missing parameter: {str(e)}"
        )

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    remote_ip = request.remote
    
    print(f"WebSocket connection from {remote_ip}")
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                await handle_websocket_message(ws, remote_ip, data)
            elif msg.type == WSMsgType.ERROR:
                print(f"WebSocket error: {ws.exception()}")
                
    finally:
        print(f"WebSocket closed for {remote_ip}")
        await ws.close()
    
    return ws

async def handle_websocket_message(ws, remote_ip, data):
    request_url = data.get("RequestURL")
    
    if request_url == "/LAPI/V1.0/System/UpServer/Keepalive":
        print(f"Keep-alive from {remote_ip}")
        response = {
            "ResponseURL": request_url,
            "ResponseCode": 0,
            "ResponseString": "Success",
            "Cseq": data.get("Cseq"),
            "Data": {
                "Timestamp": int(time.time()),
                "Timeout": KEEP_ALIVE_INTERVAL
            }
        }
        await ws.send_str(json.dumps(response))
        
    elif request_url == "/LAPI/V1.0/System/UpServer/Unregister":
        print(f"Unregister request from {remote_ip}")
        await ws.close()

app = web.Application()
app.add_routes([
    web.get(REGISTER_PATH, handle_http),
    web.get("/ws", websocket_handler)
])

if __name__ == "__main__":
    web.run_app(app, host="192.168.1.13", port=8080)