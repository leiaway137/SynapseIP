import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import GeneratedReport

engine = create_engine('sqlite:///gemini_sources_migrated.db')
Session = sessionmaker(bind=engine)
session = Session()

reports = session.query(GeneratedReport).all()
invalid = []
for r in reports:
    try:
        json.loads(r.report_data)
    except Exception as e:
        invalid.append((r.id, e))

print(f"Total reports: {len(reports)}")
print(f"Invalid JSON reports: {len(invalid)}")
for i, e in invalid:
    print(f"Report ID {i}: {e}")
