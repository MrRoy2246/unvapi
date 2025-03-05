import asyncio
import websockets
import json
import hmac
import hashlib
import base64
import time
import random
import urllib.parse
from concurrent.futures import ThreadPoolExecutor  # For KeepAliveThread equivalent

class WebSocketHandler:
    """
    Python version of the WebSocketHandler.java class
    """

    SECRET = "123456"
    LAPI_REGISTER = "/LAPI/V1.0/System/UpServer/Register"
    LAPI_KEEPALIVE = "/LAPI/V1.0/System/UpServer/Keepalive"
    LAPI_UNREGISTER = "/LAPI/V1.0/System/UpServer/Unregister"

    def __init__(self):
        self.handshaker = None
        self.keep_alive_executor = ThreadPoolExecutor(max_workers=3) # thread pool for the keep alive threads

    async def channelRead(self, websocket, path):
        """
        Handles incoming WebSocket messages.  Mimics the channelRead function from Java.
        """
        try:
            print(f"New connection from {websocket.remote_address}")
            # Parse the URL to determine whether this is a registration request or a websocket connection
            path =str(path)
            parsed_url = urllib.parse.urlparse(path)

            if parsed_url.path == self.LAPI_REGISTER:
                # Mimicking the initial registration handshake
                await self.handle_http_register(websocket)

            elif parsed_url.path.startswith(self.LAPI_REGISTER):
                # Mimicking the second registration handshake
                query_params = urllib.parse.parse_qs(parsed_url.query)
                await self.handle_http_register_vendor(websocket, query_params)

            else:
                #Handle a normal websocket connection
                async for message in websocket:
                    await self.handleWebSocketRequest(websocket, message)

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed abruptly: {e}")  # Handle disconnections more gracefully.
        except Exception as e:
            self.exceptionCaught(websocket, e) # call the exception handling function
        finally:
            self.handlerRemoved(websocket) # remove from the channel

    async def handle_http_register(self, websocket):
        """
        Handles the initial HTTP registration request.
        """
        object = {"Nonce": self.getCnonce()}
        response_body = json.dumps(object)
        #Cannot directly send an HTTP response using websockets.  Need to send a message
        await websocket.send(response_body)
        print(f"Sent initial registration challenge to {websocket.remote_address}")


    async def handle_http_register_vendor(self, websocket, query_params):
        """
        Handles the second HTTP registration request with vendor information.
        """
        try:
            Vendor = query_params.get("Vendor", [None])[0] # use none as default, get first element in list
            DeviceType = query_params.get("DeviceType", [None])[0]
            Devicecode = query_params.get("DeviceCode", [None])[0]
            Algorithm = query_params.get("Algorithm", [None])[0]
            Nonce = query_params.get("Nonce", [None])[0]
            Cnonce = query_params.get("Cnonce", [None])[0] if "Cnonce" in query_params else "" # handle if Cnonce is not contained
            Sign = query_params.get("Sign", [None])[0]

            if None in (Vendor, DeviceType, Devicecode, Algorithm, Nonce, Sign):
                print("Missing parameters in registration request")
                await websocket.close(code=4000, reason="Missing parameters")
                return

            decoded_url = urllib.parse.unquote(Sign)
            decoded_url = decoded_url.replace(" ", "+")
            print(f"Certified Signature: {decoded_url}")

            pstr = f"{Vendor}/{DeviceType}/{Devicecode}/{Algorithm}/{Nonce}"

            # Generate server-side signature
            sha256_HMAC = hmac.new(self.SECRET.encode("utf-8"), pstr.encode("utf-8"), hashlib.sha256)
            encodeStr = base64.b64encode(sha256_HMAC.digest()).decode("utf-8")

            if not hmac.compare_digest(encodeStr, decoded_url): # hmac.compare_digest to prevent timing attacks
                print(f"Authentication failed: {encodeStr}")
                object = {"Nonce": self.getCnonce()}
                await websocket.send(json.dumps(object))  # Send back a challenge
                return

            print("Authentication successful")
            object = {"Cnonce": Cnonce, "Resign": encodeStr}
            await websocket.send(json.dumps(object)) # send back the Cnonce and Resign values
            self.handlerAdded(websocket) # now that the handshake is complete, add the handler

        except Exception as e:
            print(f"Error during vendor registration: {e}")
            await websocket.close(code=5000, reason="Internal server error")


    async def handleWebSocketRequest(self, websocket, message):
        """
        Handles incoming WebSocket frames.
        """
        try:
            jsonObject = json.loads(message)
            request_url = jsonObject.get("requestURL")

            if request_url == self.LAPI_KEEPALIVE:
                print(f"The server received a device's keep alive request: {request_url}")
                # Use threads to receive keep alive information
                # NOTE: The KeepLiveThread needs to be adapted to run in Python.
                # The example uses a basic thread pool to execute the logic asynchronously
                self.keep_alive_executor.submit(self.keep_alive_task, websocket, jsonObject)

            elif request_url == self.LAPI_UNREGISTER:
                print(f"{websocket.remote_address} Device disconnected")
                await websocket.close()

            else:
                print(f"Received unknown request: {request_url}")

        except json.JSONDecodeError:
            print("Invalid JSON received")
        except Exception as e:
            self.exceptionCaught(websocket, e)

    def keep_alive_task(self, websocket, jsonObject):
      '''
      This is the logic previously performed by the keepAliveThread.
      Since we cannot directly translate the Java thread, this simulates
      the thread with a task submitted to the threadpool.
      '''
      try:
        print(f"Processing Keep-Alive from {websocket.remote_address}: {jsonObject}")
        #Simulate some processing
        time.sleep(2)
        print(f"Keep-Alive processing complete for {websocket.remote_address}")

      except Exception as e:
        print(f"Error during keep-alive processing {websocket.remote_address}: {e}")


    def handlerAdded(self, websocket):
        """
        Called when a handler is added to the pipeline (connection established).
        """
        print(f"{websocket.remote_address} The device is connected")
        self.channelActive(websocket) # call channel active

    def handlerRemoved(self, websocket):
        """
        Called when a handler is removed from the pipeline (connection closed).
        """
        print(f"{websocket.remote_address} The device has been removed")
        self.channelInactive(websocket) # call channel inactive

    def channelActive(self, websocket):
        """
        Called when a channel becomes active (connection is ready for communication).
        """
        print(f"Client joined connection: {websocket.remote_address}")

    def channelInactive(self, websocket):
        """
        Called when a channel becomes inactive (connection is closed).
        """
        print(f"Client disconnected: {websocket.remote_address}")

    def exceptionCaught(self, websocket, error):
        """
        Handles exceptions that occur during channel processing.
        """
        print(f"Exception occurred: {error}")
        asyncio.create_task(websocket.close())  # Close the connection

    def getCnonce(self):
        """
        Calculates a cnonce value (client nonce).
        """
        d = random.random()
        d1 = time.time()
        x = d * d1
        return str(int(x))


async def websocket_server(ip, port):
    """
    Main function to run the WebSocket server.  Mimics the Websocket.java class
    """
    print("Starting websocket server...")

    async def handler(websocket,path=None):
        """
        The handler that will be called for each new websocket.
        """
        websocket_handler = WebSocketHandler() #Create an instance for each connection.
        await websocket_handler.channelRead(websocket,path)


    try:
        # Start the WebSocket server
        async with websockets.serve(handler, ip, port): 
            # as server:
            print(f"WebSocket server started successfully on {ip}:{port}")
            await asyncio.Future()  # Run forever
    except OSError as e:
        print(f"The webSocket server failed to start: {e}.  Please check the IP/port settings")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Websocket Server closed.")


if __name__ == "__main__":
    # Set the IP and port
    IP = "192.168.1.13"
    PORT = 8080

    # Run the WebSocket server
    asyncio.run(websocket_server(IP, PORT))
