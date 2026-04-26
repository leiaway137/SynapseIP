"""
One-time migration script: Neon PostgreSQL → SQLite
Connects to Neon, reads all tables, writes to a local SQLite database.

Usage:
    python migrate_neon_to_sqlite.py [--output path/to/output.db]
    
    Reads DATABASE_URL from .env for the Neon connection string.
    Defaults output to ./gemini_sources.db
"""

import os
import sys
import json
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# ---- Configuration ----
NEON_URL = os.environ.get("DATABASE_URL") or os.environ.get("MIGRATION_SOURCE_URL")
OUTPUT_PATH = "./gemini_sources_migrated.db"

# Allow override via CLI arg
if "--output" in sys.argv:
    idx = sys.argv.index("--output")
    if idx + 1 < len(sys.argv):
        OUTPUT_PATH = sys.argv[idx + 1]

if not NEON_URL:
    print("❌ ERROR: No DATABASE_URL or MIGRATION_SOURCE_URL found in environment.")
    print("   Make sure your .env file contains the Neon connection string.")
    sys.exit(1)

print(f"📡 Connecting to Neon PostgreSQL...")
print(f"   Host: {NEON_URL.split('@')[1].split('/')[0] if '@' in NEON_URL else 'unknown'}")

# ---- Connect to source (Neon PostgreSQL) ----
pg_engine = create_engine(NEON_URL, pool_pre_ping=True)
PgSession = sessionmaker(bind=pg_engine)
pg_session = PgSession()

# ---- Connect to target (SQLite) ----
SQLITE_URL = f"sqlite:///{OUTPUT_PATH}"
sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SqliteSession = sessionmaker(bind=sqlite_engine)

# ---- Define table migration order (respects foreign keys) ----
TABLES = [
    "users",
    "projects",
    "gemini_sources",
    "generated_reports",
    "architect_blueprints",
    "project_themes",
    "system_configs",
    "chat_history",
    "token_logs",
]

print(f"\n🔍 Inspecting Neon database...")
pg_inspector = inspect(pg_engine)
existing_tables = pg_inspector.get_table_names()
print(f"   Found tables: {existing_tables}")

# ---- Create SQLite schema by importing models from main.py ----
# We import Base after engine creation to avoid conflicts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Manually create tables in SQLite using the same DDL from Neon
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, MetaData
from sqlalchemy.orm import declarative_base

SqliteBase = declarative_base()

class User(SqliteBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)

class Project(SqliteBase):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    suggested_themes = Column(Text, nullable=True)
    notes_since_last_check = Column(Integer, default=0)
    current_vibe_step = Column(Integer, default=0)
    is_consistent = Column(Boolean, default=False)
    onboarding_config = Column(Text, nullable=True)
    followup_history = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class GeminiSource(SqliteBase):
    __tablename__ = "gemini_sources"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    title = Column(String, index=True)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_url = Column(String, index=True)
    processed = Column(Boolean, default=False)
    short_memory = Column(Text, nullable=True)

class GeneratedReport(SqliteBase):
    __tablename__ = "generated_reports"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    report_data = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ArchitectBlueprint(SqliteBase):
    __tablename__ = "architect_blueprints"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    blueprint_data = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ProjectTheme(SqliteBase):
    __tablename__ = "project_themes"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    theme_name = Column(String, index=True)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SystemConfig(SqliteBase):
    __tablename__ = "system_configs"
    key = Column(String, primary_key=True, index=True)
    value = Column(String)

class ChatHistory(SqliteBase):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    phase = Column(String)
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class TokenLog(SqliteBase):
    __tablename__ = "token_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    action = Column(String, index=True)
    model_name = Column(String)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ---- Create all tables in SQLite ----
print(f"\n📦 Creating SQLite database at: {OUTPUT_PATH}")
SqliteBase.metadata.create_all(bind=sqlite_engine)
sqlite_session = SqliteSession()

# ---- Migrate data table by table ----
print(f"\n🚀 Starting migration...\n")
total_rows = 0
summary = {}

for table_name in TABLES:
    if table_name not in existing_tables:
        print(f"   ⏭️  {table_name}: not found in Neon, skipping")
        summary[table_name] = 0
        continue
    
    try:
        rows = pg_session.execute(text(f"SELECT * FROM {table_name}")).fetchall()
        columns = pg_session.execute(text(f"SELECT * FROM {table_name} LIMIT 0")).keys()
        col_names = list(columns)
        
        if not rows:
            print(f"   📭 {table_name}: 0 rows (empty)")
            summary[table_name] = 0
            continue
        
        # Insert into SQLite
        for row in rows:
            row_dict = dict(zip(col_names, row))
            sqlite_session.execute(
                text(f"INSERT OR REPLACE INTO {table_name} ({', '.join(col_names)}) VALUES ({', '.join([':' + c for c in col_names])})"),
                row_dict
            )
        
        sqlite_session.commit()
        count = len(rows)
        total_rows += count
        summary[table_name] = count
        print(f"   ✅ {table_name}: {count} rows migrated")
        
    except Exception as e:
        print(f"   ❌ {table_name}: ERROR - {e}")
        summary[table_name] = f"ERROR: {e}"
        sqlite_session.rollback()

# ---- Summary ----
print(f"\n{'='*50}")
print(f"📊 Migration Summary")
print(f"{'='*50}")
for table, count in summary.items():
    status = f"{count} rows" if isinstance(count, int) else count
    print(f"   {table:25s} → {status}")
print(f"{'='*50}")
print(f"   Total rows migrated: {total_rows}")
print(f"   Output file: {OUTPUT_PATH}")
print(f"   Output size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")
print(f"{'='*50}")

# Cleanup
pg_session.close()
sqlite_session.close()
print(f"\n✅ Migration complete!")
