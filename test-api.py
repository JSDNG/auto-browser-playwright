import requests

# Cấu hình
BASE_URL = "http://127.0.0.1:2268"
PROFILE_ID = "6898c8f7effa52a76ed48168"   # thay bằng ID thật của bạn

# Endpoint start profile
url = f"{BASE_URL}/profiles/start/{PROFILE_ID}"

print("Testing HMA API:", url)

try:
    response = requests.post(url, timeout=30)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
except Exception as e:
    print("Error:", e)
