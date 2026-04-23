from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN onboarding_config TEXT;"))
            conn.commit()
            print("Successfully added onboarding_config to projects")
        except Exception as e:
            print("Migration probably already ran or failed:", e)
else:
    print("No DATABASE_URL found")
