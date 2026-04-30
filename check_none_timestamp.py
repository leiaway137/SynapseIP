from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import GeneratedReport, ArchitectBlueprint

engine = create_engine('sqlite:///gemini_sources_migrated.db')
Session = sessionmaker(bind=engine)
session = Session()

print("Reports with none:", session.query(GeneratedReport).filter(GeneratedReport.timestamp == None).count())
print("Blueprints with none:", session.query(ArchitectBlueprint).filter(ArchitectBlueprint.timestamp == None).count())
