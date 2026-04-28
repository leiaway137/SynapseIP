import asyncio
from main import SessionLocal, GeminiSource, process_single_card

async def test():
    db = SessionLocal()
    unprocessed_cards = db.query(GeminiSource).filter(GeminiSource.processed == False).limit(2).all()
    print(f"Found {len(unprocessed_cards)} unprocessed cards.")
    
    tasks = []
    for c in unprocessed_cards:
        c_dict = {
            "id": c.id,
            "title": c.title,
            "content": c.content,
            "project_id": c.project_id
        }
        tasks.append(process_single_card(c_dict))
    
    print("Starting processing...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print("Results:", results)

asyncio.run(test())
