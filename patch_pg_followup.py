from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("No DATABASE_URL found in .env")
    exit(1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE projects ADD COLUMN followup_history TEXT;"))
        conn.commit()
        print("Successfully added followup_history to Postgres database!")
    except Exception as e:
        print(f"Error executing alter table: {e}")
