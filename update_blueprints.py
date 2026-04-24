import re
import psycopg2

conn = psycopg2.connect('postgresql://neondb_owner:npg_dyko7SLcmeO8@ep-tiny-queen-an1qw5a7.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require')
cur = conn.cursor()
cur.execute("SELECT id, blueprint_data FROM architect_blueprints")
rows = cur.fetchall()

def replace_header(match):
    idx = int(match.group(1)) - 1
    title = match.group(2)
    return f"## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='{idx}'> Step {idx+1}: {title}</label>\n\n"

for row in rows:
    bp_id = row[0]
    data = row[1]
    
    # regex to match "## [ ] Step 1: Some Title\n\n"
    # Note: earlier it was f"## [ ] Step {i+1}: {chapter_title}\n\n"
    new_data = re.sub(r'##\s*\[\s*\]\s*Step\s+(\d+):\s*(.+)\n\n', replace_header, data)
    
    if new_data != data:
        cur.execute("UPDATE architect_blueprints SET blueprint_data = %s WHERE id = %s", (new_data, bp_id))

conn.commit()
conn.close()
print("Updated blueprints")
