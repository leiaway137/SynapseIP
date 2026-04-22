import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("NO DATABASE URL FOUND")
    exit(1)

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    try:
        # Check how many are currently True
        res = conn.execute(text("SELECT count(*) FROM gemini_sources WHERE processed = True")).scalar()
        print(f"Found {res} processed cards. Resetting to False...")
        
        conn.execute(text("UPDATE gemini_sources SET processed = False"))
        conn.commit()
        
        res_after = conn.execute(text("SELECT count(*) FROM gemini_sources WHERE processed = False")).scalar()
        print(f"Success: {res_after} cards are now marked as unprocessed.")
    except Exception as e:
        print("Error:", e)
