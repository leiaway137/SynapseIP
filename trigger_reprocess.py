import requests
import sys

BASE_URL = "https://synapseip-1ncu.onrender.com"
USERNAME = "leiaway"
PASSWORD = "password" # Adjust if necessary

print(f"Logging into {BASE_URL} as {USERNAME}...")
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    data={"username": USERNAME, "password": PASSWORD}
)

if response.status_code != 200:
    print("Login failed:", response.text)
    sys.exit(1)

token = response.json()["access_token"]
print("Login successful! Triggering reprocessing...")

headers = {"Authorization": f"Bearer {token}"}

# Trigger reprocess
resp = requests.post(f"{BASE_URL}/api/admin/reprocess-all", headers=headers)
if resp.status_code == 200:
    print("Success:", resp.json())
else:
    print("Failed:", resp.status_code, resp.text)
