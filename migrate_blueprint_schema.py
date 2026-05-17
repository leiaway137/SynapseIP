"""
Migration script to add blueprint_slug column to architect_blueprints table
"""
import sqlite3
import os

def migrate():
    db_path = "./synapse.db"
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if blueprint_slug column exists
        cursor.execute("PRAGMA table_info(architect_blueprints)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "blueprint_slug" in columns:
            print("✅ blueprint_slug column already exists")
            return
        
        print("Adding blueprint_slug column to architect_blueprints table...")
        
        # Add the column (nullable, no UNIQUE constraint for migration compatibility)
        cursor.execute("""
            ALTER TABLE architect_blueprints 
            ADD COLUMN blueprint_slug TEXT
        """)
        
        conn.commit()
        print("✅ Successfully added blueprint_slug column")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()