import os
from sqlalchemy import create_engine, text

DATA_DIR = os.environ.get("DATA_DIR", ".")
target_db_path = os.path.join(DATA_DIR, 'gemini_sources.db')
engine = create_engine(f"sqlite:///{target_db_path}")

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("""
            CREATE TABLE framework_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                normalized_name VARCHAR NOT NULL UNIQUE,
                content TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """))
            conn.execute(text("CREATE INDEX ix_framework_templates_normalized_name ON framework_templates (normalized_name)"))
            conn.execute(text("CREATE INDEX ix_framework_templates_id ON framework_templates (id)"))
            conn.commit()
            print("Successfully created framework_templates table.")
        except Exception as e:
            print(f"Error creating table: {e}")

if __name__ == "__main__":
    migrate()
