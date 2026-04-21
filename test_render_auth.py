import httpx

# 1. Login to Render
render_url = "https://synapseip-1ncu.onrender.com"
print("Logging in to Render...")
r = httpx.post(f"{render_url}/api/auth/login", data={"username": "leiaway", "password": "password"})
print("Login status:", r.status_code)
if r.status_code != 200:
    print("Failed to login! Cannot test further.")
    print(r.text)
    exit()

token = r.json()["access_token"]
print("Token retrieved!")

# 2. Access Admin metrics
print("Accessing /api/admin/metrics...")
r2 = httpx.get(f"{render_url}/api/admin/metrics", headers={"Authorization": f"Bearer {token}"})
print("Metrics status:", r2.status_code)
print("Response:", r2.text[:300])

