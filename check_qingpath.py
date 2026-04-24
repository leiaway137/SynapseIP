import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.environ.get("DATABASE_URL"))

with engine.connect() as conn:
    # Find QingPath project
    project = conn.execute(text("SELECT id, name FROM projects WHERE name ILIKE '%QingPath%'")).first()
    if not project:
        print("Project QingPath not found.")
    else:
        print(f"Found Project: {project.name} (ID: {project.id})")
        # Count total sources
        total = conn.execute(text("SELECT COUNT(*) FROM gemini_sources WHERE project_id = :pid"), {"pid": project.id}).scalar()
        # Count sources with short_memory
        processed = conn.execute(text("SELECT COUNT(*) FROM gemini_sources WHERE project_id = :pid AND short_memory IS NOT NULL AND short_memory != ''"), {"pid": project.id}).scalar()
        
        print(f"Total Sources: {total}")
        print(f"Sources with Short Memory: {processed}")
