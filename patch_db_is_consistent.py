import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("No DATABASE_URL found.")
    exit(1)

engine = create_engine(db_url)
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE projects ADD COLUMN is_consistent BOOLEAN DEFAULT FALSE;"))
        conn.commit()
        print("Successfully added 'is_consistent' to projects table.")
    except Exception as e:
        print(f"Error: {e}")
