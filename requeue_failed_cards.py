import os
import sys
from dotenv import load_dotenv

# Load env before importing main
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from main import GeminiSource, Project

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("No DATABASE_URL found.")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Find Qingpath project
    qingpath = db.query(Project).filter(Project.name.ilike("%Qingpath%")).first()
    if not qingpath:
        print("Qingpath project not found!")
        sys.exit(1)
        
    print(f"Found Qingpath Project ID: {qingpath.id}")

    # Find all failed cards
    failed_cards = db.query(GeminiSource).filter(
        GeminiSource.processed == True,
        GeminiSource.title.like("%Processing Failed%")
    ).all()
    
    # Also find #27 and #28 specifically, in case their titles got truncated weirdly
    specific_cards = db.query(GeminiSource).filter(GeminiSource.id.in_([27, 28])).all()
    
    cards_to_requeue = set(failed_cards + specific_cards)
    
    print(f"Found {len(cards_to_requeue)} failed/specific cards to requeue.")
    
    # We want Qingpath cards to be processed first.
    # background_processor uses order_by(GeminiSource.timestamp.asc())
    # So we set Qingpath timestamps to very old, and others to slightly less old.
    
    old_time = datetime.utcnow() - timedelta(days=365)
    
    updated_count = 0
    for card in cards_to_requeue:
        if card.processed == True: # only requeue if not already in queue
            card.processed = False
            
            # Prioritize Qingpath
            if card.project_id == qingpath.id:
                card.timestamp = old_time - timedelta(days=1) # 1 day older than the rest
            else:
                card.timestamp = old_time
            
            print(f"Requeuing Card ID: {card.id} (Project ID: {card.project_id})")
            updated_count += 1

    db.commit()
    print(f"Successfully requeued {updated_count} cards.")
    
except Exception as e:
    print("Error:", e)
    db.rollback()
finally:
    db.close()
