import sys
import os

sys.path.append(os.getcwd())
from main import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE projects ADD COLUMN current_vibe_step INTEGER DEFAULT 0;"))
        conn.commit()
        print("Successfully added current_vibe_step column.")
    except Exception as e:
        print(f"Migration error (might already exist): {e}")

