import json
from datetime import datetime

class Report:
    def __init__(self, id, timestamp):
        self.id = id
        self.timestamp = timestamp

# Test what happens when we just dump a datetime object using standard json (which FastAPI wraps)
try:
    print(json.dumps({"id": 1, "timestamp": datetime.now()}))
except Exception as e:
    print("Standard json dumps error:", type(e).__name__, e)

import fastapi.encoders
print("FastAPI encoder:", fastapi.encoders.jsonable_encoder({"id": 1, "timestamp": datetime.now()}))
