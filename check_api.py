import requests
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import User

engine = create_engine('sqlite:///gemini_sources_migrated.db')
Session = sessionmaker(bind=engine)
session = Session()

user = session.query(User).first()
if user:
    # We need a valid JWT token
    from main import create_access_token
    from datetime import timedelta
    token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=30))
    print("Token:", token)
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get("http://localhost:8000/api/projects/1/documents", headers=headers)
    print("Status:", r.status_code)
    try:
        print(json.dumps(r.json(), indent=2)[:500])
    except Exception as e:
        print(r.text)
else:
    print("No user found")
