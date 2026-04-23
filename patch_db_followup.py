import sqlite3
import os

DATA_DIR = os.environ.get("DATA_DIR", ".")
db_path = os.path.join(DATA_DIR, "gemini_sources.db")

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add the followup_history column
        cursor.execute("ALTER TABLE projects ADD COLUMN followup_history TEXT;")
        print("Successfully added 'followup_history' column to 'projects' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column 'followup_history' already exists.")
        else:
            print("Error:", e)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
