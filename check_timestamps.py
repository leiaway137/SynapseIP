from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import GeneratedReport, ArchitectBlueprint

engine = create_engine('sqlite:///gemini_sources_migrated.db')
Session = sessionmaker(bind=engine)
session = Session()

reports = session.query(GeneratedReport).limit(5).all()
print("Reports:")
for r in reports:
    print(r.id, repr(r.timestamp), type(r.timestamp))

blueprints = session.query(ArchitectBlueprint).limit(5).all()
print("\nBlueprints:")
for b in blueprints:
    print(b.id, repr(b.timestamp), type(b.timestamp))
