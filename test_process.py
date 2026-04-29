import asyncio
import os
import json
from dotenv import load_dotenv
load_dotenv()

from main import process_single_card, SessionLocal, GeminiSource, project_locks
from sqlalchemy.orm import Session

async def main():
    print("Fetching one failed card...")
    db = SessionLocal()
    card = db.query(GeminiSource).filter(GeminiSource.title.like("⚠️ Processing Failed%")).first()
    if not card:
        print("No failed cards found.")
        return
        
    print(f"Testing Card ID {card.id}")
    card_dict = {
        'id': card.id,
        'title': card.title,
        'content': card.content,
        'project_id': card.project_id
    }
    db.close()
    
    try:
        await asyncio.wait_for(process_single_card(card_dict), timeout=600.0)
        print("Successfully processed!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("FAILED:", e)

if __name__ == "__main__":
    asyncio.run(main())
