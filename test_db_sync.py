import httpx
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from main import User, SQLALCHEMY_DATABASE_URL

# 1. Register fake account mathematically unique to force Render to record it
fake_username = f"render_sync_test_{uuid.uuid4().hex[:6]}"
print("Registering fake username on Render:", fake_username)
r = httpx.post("https://synapseip-1ncu.onrender.com/api/auth/register", json={"username": fake_username, "password": "password"})
print("Render Register Status:", r.status_code)

# 2. Query Neon DB locally to see if it appeared
print("Querying Neon PostgreSQL DB for:", fake_username)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
with Session(engine) as db:
    user = db.query(User).filter_by(username=fake_username).first()
    if user:
        print("✅ SUCCESS! Render is 100% connected to Neon DB!")
    else:
        print("❌ FAILED! The user was NOT mirrored to Neon. Render is using a rogue SQLite instance!")
