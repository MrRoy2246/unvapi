
#device info api
import requests
from requests.auth import HTTPDigestAuth

# IPC Camera details
IPC_BASE_URL = "http://192.168.1.246"  # Replace with actual IPC IP
DEVICE_INFO_URL = f"{IPC_BASE_URL}/LAPI/V1.0/System/DeviceInfo"
# Device credentials
USERNAME = "admin"  
PASSWORD = "Accelx#123456" 
def get_device_info():
    """
    Fetch device information from IPC LiteAPI.
    """
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(DEVICE_INFO_URL, headers=headers, auth=HTTPDigestAuth(USERNAME, PASSWORD), timeout=10)
        response.raise_for_status() 
        print("✅ API Call Successful!")
        print(f'Status : {response.status_code}')
        print(response.json()) 
    except requests.exceptions.HTTPError as err:
        print(f"❌ HTTP Error {response.status_code}: {err}")
    except requests.exceptions.ConnectionError as err:
        print("❌ Connection Error: Unable to reach the device.")     
        print(f"Error Details: {err}")
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: The request took too long to respond.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
#run the api
get_device_info()
    

