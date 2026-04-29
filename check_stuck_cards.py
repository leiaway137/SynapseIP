import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("NO DATABASE_URL")
    exit()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

from sqlalchemy import text
res = db.execute(text("SELECT id, title, processed, project_id FROM gemini_sources WHERE processed = false")).fetchall()
print(f"Total unprocessed cards: {len(res)}")
for row in res:
    print(f"ID: {row[0]}, Title: {row[1]}, processed: {row[2]}")

db.close()
