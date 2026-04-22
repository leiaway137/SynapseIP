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
        conn.execute(text("ALTER TABLE projects ADD COLUMN suggested_themes TEXT;"))
        conn.commit()
        print("Success: Added suggested_themes column.")
    except Exception as e:
        print("Error or already exists:", e)
