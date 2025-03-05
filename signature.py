import hmac
import hashlib
import base64

SECRET = "123456"
vendor = "TestVendor"
device_type = "TestDevice"
device_code = "12345"
algorithm = "HMAC-SHA256"
nonce = "1741158917"  # Use the actual nonce from the first API response

message = f"{vendor}/{device_type}/{device_code}/{algorithm}/{nonce}".encode()
signature = base64.b64encode(hmac.new(SECRET.encode(), message, hashlib.sha256).digest()).decode()

print("Generated Sign:", signature)
