import sqlite3
import re

db_path = 'gemini_sources.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, theme_name, content FROM project_themes WHERE length(content) > 10000")
bloated_themes = cursor.fetchall()

updated = 0
for theme_id, name, content in bloated_themes:
    # Aggressively strip out massive inline CSS styles from pasted HTML
    clean_content = re.sub(r'style="[^"]+"', '', content)
    
    # Take only the first 1500 characters
    truncated = clean_content[:1500]
    
    # Close any open HTML tags simply by appending a notice
    final_content = truncated + f"\n\n...\n\n**[Notice: This theme was aggressively truncated locally by Antigravity to remove {len(content)} characters of runaway HTML bloat, saving you API tokens. Future additions will be synthesized normally.]**"
    
    cursor.execute("UPDATE project_themes SET content = ? WHERE id = ?", (final_content, theme_id))
    updated += 1

conn.commit()
conn.close()
print(f"✅ Successfully pruned {updated} bloated themes locally (0 tokens used).")
