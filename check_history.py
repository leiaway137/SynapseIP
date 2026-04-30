import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Project

engine = create_engine('sqlite:///gemini_sources_migrated.db')
Session = sessionmaker(bind=engine)
session = Session()

projects = session.query(Project).all()
invalid = []
for p in projects:
    try:
        if p.followup_history:
            json.loads(p.followup_history)
    except Exception as e:
        invalid.append((p.id, p.followup_history, e))

print(f"Total projects: {len(projects)}")
print(f"Invalid history projects: {len(invalid)}")
for i, h, e in invalid:
    print(f"Project ID {i}: {e}")
    print(f"Content: {h}")
