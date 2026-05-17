import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from main import ArchitectDraftState, SessionLocal, db_url

engine = create_engine(db_url)
db = SessionLocal()

state = db.query(ArchitectDraftState).filter(ArchitectDraftState.project_id == 4).first()
if state:
    print(f"Current loop: {state.current_loop}")
    state.current_loop = 2
    db.commit()
    print("Reset to loop 2 successfully. Please refresh the browser.")
else:
    print("State not found")

db.close()
