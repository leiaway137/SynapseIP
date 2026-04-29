from main import SessionLocal, GeminiSource
db = SessionLocal()
print("Total SQLite cards:", db.query(GeminiSource).count())
db.close()
