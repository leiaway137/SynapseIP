import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from main import User, SQLALCHEMY_DATABASE_URL

print("Connecting to:", SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
with Session(engine) as db:
    user = db.query(User).filter_by(username="leiaway").first()
    if user:
        user.is_admin = True
        db.commit()
        print("SUCCESS! User 'leiaway' is now an Administrator.")
    else:
        print("FAILED: User 'leiaway' not found in database.")
