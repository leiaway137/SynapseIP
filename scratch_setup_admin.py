import sys
import os

# Ensure the current directory is in sys.path
sys.path.append(os.getcwd())

from main import SessionLocal, User, get_password_hash, Base, engine

# Ensure tables are created
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    user = db.query(User).filter(User.username == "leiaway").first()
    if not user:
        pwd = get_password_hash("synapseadmin")
        user = User(username="leiaway", password_hash=pwd, is_admin=True)
        db.add(user)
        db.commit()
        print("Successfully created administrator 'leiaway' with password 'synapseadmin'")
    else:
        user.is_admin = True
        db.commit()
        print("User 'leiaway' already exists. Updated to administrator.")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
