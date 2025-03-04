#!/usr/bin/env python3
# All required dependencies and imports
import hmac
import hashlib
import base64
import json
import random
import time
import datetime
import threading
import decimal
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote, urlparse, parse_qs

# Dummy implementations of Netty related classes and utilities

class ReferenceCountUtil:
    @staticmethod
    def release(msg):
        # In this Python simulation, no action is needed for releasing the message.
        pass

class Channel:
    def __init__(self, remote_address):
        self._remote_address = remote_address

    def remoteAddress(self):
        return self._remote_address

    def writeAndFlush(self, msg):
        # In this simulation, simply print the message being sent.
        print("Sending message:", msg)

    def write(self, msg):
        # In this simulation, simply print the message being written.
        print("Writing message:", msg)

    def close(self):
        print("Closing channel with remote address:", self._remote_address)

class ChannelHandlerContext:
    def __init__(self, channel):
        self._channel = channel

    def channel(self):
        return self._channel

    def flush(self):
        # In this simulation, flush is a no-op.
        pass

class DecoderResult:
    def __init__(self, success=True):
        self._success = success

    def isSuccess(self):
        return self._success

class FullHttpRequest:
    def __init__(self, uri, headers, decoder_success=True):
        self.uri = uri
        self._headers = headers  # dictionary
        self._decoder_result = DecoderResult(decoder_success)

    def headers(self):
        return self._headers

    def decoderResult(self):
        return self._decoder_result

class FullHttpResponse:
    def __init__(self, http_version, status, content=b''):
        self.http_version = http_version
        self.status = status
        self.content = content  # bytes
        self._headers = {}

    def headers(self):
        return self._headers

class DefaultFullHttpResponse(FullHttpResponse):
    def __init__(self, http_version, status, content=b''):
        super().__init__(http_version, status, content)

class HttpVersion:
    HTTP_1_1 = "HTTP/1.1"

class HttpResponseStatus:
    BAD_REQUEST = "400 Bad Request"
    UNAUTHORIZED = "401 Unauthorized"
    # For successful responses, we use 200 OK
    OK = "200 OK"

    def __init__(self, status):
        self.status = status

    def code(self):
        # Return numeric code from status string
        return int(self.status.split()[0])

    def __str__(self):
        return self.status

class ByteBuf:
    # In this simulation, ByteBuf is just bytes wrapper.
    def __init__(self, data):
        self.data = data

    def release(self):
        # No op in Python simulation.
        pass

class Unpooled:
    @staticmethod
    def copiedBuffer(data, charset='utf-8'):
        if isinstance(data, str):
            return data.encode(charset)
        elif isinstance(data, bytes):
            return data
        else:
            return str(data).encode(charset)

class CharsetUtil:
    UTF_8 = "utf-8"

class HttpHeaderNames:
    CONTENT_TYPE = "Content-Type"

class HttpUtil:
    @staticmethod
    def isKeepAlive(req):
        # In this simulation, we assume header 'Connection' with value 'keep-alive' means keep alive;
        # Otherwise, not.
        connection = req.headers().get("Connection", "").lower()
        return connection == "keep-alive"

    @staticmethod
    def setContentLength(res, length):
        res.headers()["Content-Length"] = str(length)

class ChannelFuture:
    def __init__(self, success=True):
        self._success = success

    def isSuccess(self):
        return self._success

    def addListener(self, listener):
        listener.operationComplete(self)

class ChannelFutureListener:
    # A simple listener interface
    def operationComplete(self, future):
        pass

class QueryStringDecoder:
    def __init__(self, uri):
        self.uri = uri
        parsed = urlparse(uri)
        self._parameters = parse_qs(parsed.query)

    def parameters(self):
        return self._parameters

class WebSocketFrame:
    # Base class for WebSocket frames.
    def __init__(self, content=b''):
        self.content = content

class CloseWebSocketFrame(WebSocketFrame):
    def __init__(self, content=b''):
        super().__init__(content)

    def retain(self):
        # In this simulation, return self.
        return self

class PingWebSocketFrame(WebSocketFrame):
    def __init__(self, content=b''):
        super().__init__(content)

class PongWebSocketFrame(WebSocketFrame):
    def __init__(self, content=b''):
        super().__init__(content)

class TextWebSocketFrame(WebSocketFrame):
    def __init__(self, text):
        super().__init__(text.encode(CharsetUtil.UTF_8))
        self._text = text

    def text(self):
        return self._text

class WebSocketServerHandshaker:
    def handshake(self, channel, req):
        # Simulate handshake success and return a ChannelFuture
        return ChannelFuture(success=True)

    def close(self, channel, frame):
        print("Closing WebSocket connection for channel:", channel.remoteAddress())

class WebSocketServerHandshakerFactory:
    def __init__(self, webSocketURL, subprotocols, allowExtensions, maxFrameSize):
        self.webSocketURL = webSocketURL
        self.subprotocols = subprotocols
        self.allowExtensions = allowExtensions
        self.maxFrameSize = maxFrameSize

    def newHandshaker(self, req):
        # In this simulation, always return a new handshaker.
        return WebSocketServerHandshaker()

    @staticmethod
    def sendUnsupportedVersionResponse(channel):
        print("Sending unsupported WebSocket version response to channel:", channel.remoteAddress())

# Dummy implementations for external classes

class WebsocketReq:
    # Simulated WebsocketReq class with a getRequestURL method.
    def __init__(self, **kwargs):
        # We assume the requestURL field is provided with exact key 'requestURL'
        # If key "requestURL" is not present, use empty string.
        self.requestURL = kwargs.get("requestURL", "")

    def getRequestURL(self):
        return self.requestURL

class KeepLiveThread(threading.Thread):
    # Simulated keep alive thread
    def __init__(self, channel, jsonObject):
        threading.Thread.__init__(self)
        self.channel = channel
        self.jsonObject = jsonObject

    def run(self):
        # Simulated keep alive processing.
        print("Executing KeepLiveThread for channel:", self.channel.remoteAddress())
        print("Keep alive data:", self.jsonObject)

class KeepLiveThreadPoolExecutor:
    # Simulated thread pool executor for keep alive threads
    EXECUTOR_SERVICE = ThreadPoolExecutor(max_workers=10)

# Main WebSocketHandler class translation

class WebSocketHandler:
    # Processing class for websocket handshake
    def __init__(self):
        self.handshaker = None
    # Authentication key (consistent with device settings)
    SECRET = "123456"

    # Registration interface
    LAPI_REGISTER = "/LAPI/V1.0/System/UpServer/Register"
    # Keep alive interface
    LAPI_KEEPALIVE = "/LAPI/V1.0/System/UpServer/Keepalive"
    # Close connection
    LAPI_UNREGISTER = "/LAPI/V1.0/System/UpServer/Unregister"

    def channelRead(self, ctx, msg):
        try:
            # WebSocket connection request, accessed via HTTP request
            if isinstance(msg, FullHttpRequest):
                self.handleHttpRequest(ctx, msg)
            # WebSocket business processing, handling messages from WebSocket clients
            elif isinstance(msg, WebSocketFrame):
                self.handleWebSocketRequest(ctx, msg)
        finally:
            ReferenceCountUtil.release(msg)

    """
    After the client connects to the server (opens the connection)
    Retrieve the channle of the client and manage it in ChannelGroup
    """
    def handlerAdded(self, ctx):
        print(ctx.channel().remoteAddress(), "The device is connected, and its IP address is:", ctx.channel().remoteAddress())

    def handlerRemoved(self, ctx):
        channelIP = ctx.channel().remoteAddress()
        print(ctx.channel().remoteAddress(), "The device has been removed, and its IP address is:", channelIP)

    def channelActive(self, ctx):
        # add connections
        print("Client join connection:", ctx.channel().remoteAddress(), "\n")

    def channelInactive(self, ctx):
        print("Client disconnected:", ctx.channel().remoteAddress(), "\n")

    def channelReadComplete(self, ctx):
        ctx.flush()

    """
    Get WebSocket service information

    @param req
    @return
    """
    @staticmethod
    def getWebSocketLocation(req):
        location = req.headers().get("Host") + "/ws"
        return "ws://" + location

    # connection exception
    def exceptionCaught(self, ctx, cause):
        print("Exception occurred:", str(cause), "\n")
        ctx.channel().close()

    """
    Receive handshake requests and respond
    The only HTTP request used to create a websocket

    @param ctx
    @param req
    """
    def handleHttpRequest(self, ctx, req):
        addr = ctx.channel().remoteAddress()
        # For simulation, we assume addr is a string IP address.
        currentIP = addr if isinstance(addr, str) else addr
        uri = req.uri
        # Device request to establish connection
        print(currentIP, "Receive handshake requests, url=" + uri)
        object = {}

        # HTTP decoding failed, specify the transmission protocol to the server as Upgrade: websocket
        if (not req.decoderResult().isSuccess()) or (req.headers().get("Upgrade") != "websocket"):
            response = DefaultFullHttpResponse(HttpVersion.HTTP_1_1, HttpResponseStatus.BAD_REQUEST)
            sendHttpResponse(self, ctx, req, response)
            print("Not a request to establish a connection")
            return
        elif self.LAPI_REGISTER == uri:
            object["Nonce"] = self.getCnonce()
            fullHttpResponse = DefaultFullHttpResponse(HttpVersion.HTTP_1_1, HttpResponseStatus.UNAUTHORIZED,
                                                         Unpooled.copiedBuffer(json.dumps(object), CharsetUtil.UTF_8))
            fullHttpResponse.headers()["Content-Type"] = "application/json; charset=UTF-8"
            sendHttpResponse(self, ctx, req, fullHttpResponse)
            return
        elif self.LAPI_REGISTER + "?Vendor" in uri:
            print(currentIP, "Device initiates second registration")
            # Get request parameters
            decoder = QueryStringDecoder(req.uri)
            parameters = decoder.parameters()
            Vendor = parameters.get("Vendor", [""])[0]
            DeviceType = parameters.get("DeviceType", [""])[0]
            Devicecode = parameters.get("DeviceCode", [""])[0]
            Algorithm = parameters.get("Algorithm", [""])[0]
            Nonce = parameters.get("Nonce", [""])[0]
            Cnonce = parameters.get("Cnonce", [""])[0] if "Cnonce" in parameters else ""
            Sign = parameters.get("Sign", [""])[0]
            decodedUrl = unquote(Sign, encoding=CharsetUtil.UTF_8)
            decodedUrl = decodedUrl.replace(" ", "+")
            print("Certified Signature:" + decodedUrl)
            pstr = Vendor + "/" + DeviceType + "/" + Devicecode + "/" + Algorithm + "/" + Nonce
            # Generate server-side signature
            sha256_HMAC = hmac.new(self.SECRET.encode("utf-8"), digestmod=hashlib.sha256)
            sha256_HMAC.update(pstr.encode("utf-8"))
            hash_bytes = sha256_HMAC.digest()
            encodeStr = base64.b64encode(hash_bytes).decode("utf-8")
            if encodeStr != decodedUrl:
                print("Authentication failed:" + encodeStr)
                object["Nonce"] = self.getCnonce()
                fullHttpResponse = DefaultFullHttpResponse(HttpVersion.HTTP_1_1, HttpResponseStatus.UNAUTHORIZED,
                                                             Unpooled.copiedBuffer(json.dumps(object), CharsetUtil.UTF_8))
                fullHttpResponse.headers()["Content-Type"] = "application/json; charset=UTF-8"
                sendHttpResponse(self, ctx, req, fullHttpResponse)
                return
            else:
                print("Authentication successful")
                object["Cnonce"] = Cnonce
                object["Resign"] = encodeStr

        # Handle handshake accordingly and create a factory class for websocket handshake
        wsFactory = WebSocketServerHandshakerFactory(self.getWebSocketLocation(req), None, False, 65535 * 100)
        # Create handshake class based on factory class and HTTP request
        self.handshaker = wsFactory.newHandshaker(req)
        if self.handshaker is None:
            # Does not support websocket
            WebSocketServerHandshakerFactory.sendUnsupportedVersionResponse(ctx.channel())
        else:
            # Construct a handshake response message through it and return it to the client
            future = self.handshaker.handshake(ctx.channel(), req)
            if future.isSuccess():
                ctx.channel().writeAndFlush(TextWebSocketFrame(json.dumps(object)).text())

    """
    Receive WebSocket requests

    @param ctx
    @param req
    @throws Exception
    """
    def handleWebSocketRequest(self, ctx, req):
        currentIP = ctx.channel().remoteAddress()
        # Receive WebSocket requests, format conversion
        jsonObject = json.loads(TextWebSocketFrame(req.content.decode(CharsetUtil.UTF_8)).text())
        websocketReq = WebsocketReq(**jsonObject)

        # Determine whether it is a command to close the link
        if isinstance(req, CloseWebSocketFrame):
            # Close websocket connection
            self.handshaker.close(ctx.channel(), req.retain())
            print(ctx.channel().remoteAddress(), "Disconnect")
            return
        # Determine if it is a Ping message
        if isinstance(req, PingWebSocketFrame):
            ctx.channel().write(PongWebSocketFrame(req.content).content)
            return
        # This example supports text messages, not binary messages
        if not isinstance(req, TextWebSocketFrame):
            raise UnsupportedOperationException("Currently only supports text messages, not binary messages")
        if (ctx is None) or (self.handshaker is None) or (hasattr(ctx, "isRemoved") and ctx.isRemoved()):
            raise Exception("Handshake not successful yet, unable to send WebSocket message to device")

        if self.LAPI_KEEPALIVE == websocketReq.getRequestURL():
            print("The server received a device's keep alive request:" + websocketReq.getRequestURL())
            # Use threads to receive keep alive information
            keepLiveThread = KeepLiveThread(ctx.channel(), jsonObject)
            KeepLiveThreadPoolExecutor.EXECUTOR_SERVICE.submit(keepLiveThread.run)
        elif self.LAPI_UNREGISTER == websocketReq.getRequestURL():
            print(currentIP, "Device disconnected")

def sendHttpResponse(self, ctx, req, res):
    # BAD_QUEST (400) Response message returned by client request error
    # If the response status code is not 200
    status_code = 200
    try:
        # Try to get the numeric status code if possible
        if hasattr(res.status, "code"):
            status_code = res.status.code()
        else:
            status_code = int(str(res.status).split()[0])
    except Exception:
        status_code = 200

    if status_code != 200:
        # Put the returned status code into the cache, Unpool did not use the cache pool
        buf = Unpooled.copiedBuffer(str(res.status), CharsetUtil.UTF_8)
        # In the original code the buffer is released after use
        if hasattr(buf, "release"):
            buf.release()
        HttpUtil.setContentLength(res, len(res.content))
    # send acknowledgement
    cf = ctx.channel().writeAndFlush(res)
    # Illegal connection. Close the connection directly
    if (not HttpUtil.isKeepAlive(req)) or (status_code != 200):
        # Mimic adding listener to close the connection after future completion
        class CloseListener(ChannelFutureListener):
            def operationComplete(self, future):
                ctx.channel().close()
        if isinstance(cf, ChannelFuture):
            cf.addListener(CloseListener())

# Bind sendHttpResponse as a function in the module scope so that it can be called from the class methods.
# This is to simulate the static function call in Java.
def sendHttpResponse(handler, ctx, req, res):
    # BAD_QUEST (400) Response message returned by client request error
    status_code = 200
    try:
        if hasattr(res.status, "code"):
            status_code = res.status.code()
        else:
            status_code = int(str(res.status).split()[0])
    except Exception:
        status_code = 200
    if status_code != 200:
        buf = Unpooled.copiedBuffer(str(res.status), CharsetUtil.UTF_8)
        if hasattr(buf, "release"):
            buf.release()
        HttpUtil.setContentLength(res, len(res.content))
    cf = ctx.channel().writeAndFlush(res)
    if (not HttpUtil.isKeepAlive(req)) or (status_code != 200):
        class CloseListener(ChannelFutureListener):
            def operationComplete(self, future):
                ctx.channel().close()
        if isinstance(cf, ChannelFuture):
            cf.addListener(CloseListener())

"""
Calculate the cnonce value, which is used for authentication
"""
@staticmethod
def getCnonce():
    d = random.random()
    d1 = time.time()
    x = d * d1
    # Use Decimal to format the number without decimals
    df = decimal.Decimal(x).to_integral_value(rounding=decimal.ROUND_HALF_UP)
    return str(df)

# Attach getCnonce to WebSocketHandler class
WebSocketHandler.getCnonce = staticmethod(getCnonce)

# Custom Exception to replicate Java's UnsupportedOperationException
class UnsupportedOperationException(Exception):
    pass

# If needed, additional code can be added here to instantiate and test the WebSocketHandler.
if __name__ == "__main__":
    # Simulated test of WebSocketHandler with a FullHttpRequest for registration.
    channel = Channel("127.0.0.1")
    ctx = ChannelHandlerContext(channel)
    headers = {"Host": "localhost", "Upgrade": "websocket", "Connection": "keep-alive"}
    req = FullHttpRequest("/LAPI/V1.0/System/UpServer/Register", headers)
    handler = WebSocketHandler()
    handler.channelRead(ctx, req)
    # Simulated test of a text WebSocketFrame received after handshake.
    text_frame = TextWebSocketFrame('{"requestURL": "/LAPI/V1.0/System/UpServer/Keepalive"}')
    handler.channelRead(ctx, text_frame)
    
# End of complete translated code.
    
if __name__ == "__main__":
    # Shutdown the thread pool executor gracefully.
    KeepLiveThreadPoolExecutor.EXECUTOR_SERVICE.shutdown(wait=True)
    
# End of module
                                          
