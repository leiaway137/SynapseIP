from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from main import User, SQLALCHEMY_DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
with Session(engine) as db:
    users = db.query(User).all()
    print("ALL USERS:")
    for u in users:
        print(f"ID: {u.id}, Username: '{u.username}', Admin: {u.is_admin}")
