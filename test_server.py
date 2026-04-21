import httpx
try:
    r = httpx.get("http://localhost:8000/")
    print("STATUS:", r.status_code)
    print("BODY:", r.text[:200])
except Exception as e:
    print("ERR:", e)
