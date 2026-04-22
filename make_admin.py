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
        # Check current users
        users = conn.execute(text("SELECT id, username, is_admin FROM users")).fetchall()
        print("Current Users:")
        for u in users:
            print(f"ID: {u[0]}, Username: {u[1]}, is_admin: {u[2]}")
            
        # Update all users to be admins
        conn.execute(text("UPDATE users SET is_admin = True"))
        conn.commit()
        
        print("Success: All users are now administrators.")
    except Exception as e:
        print("Error:", e)
