import sqlite3

db_path = 'gemini_sources.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all token logs
cursor.execute("SELECT id, model_name, prompt_tokens, completion_tokens, cost FROM token_logs")
rows = cursor.fetchall()

updated_count = 0

for row in rows:
    log_id, model_name, in_toks, out_toks, old_cost = row
    
    if not in_toks:
        in_toks = 0
    if not out_toks:
        out_toks = 0
        
    cost = 0.0
    if "flash" in model_name.lower():
        if in_toks <= 128000:
            cost = (in_toks / 1000000.0) * 0.075 + (out_toks / 1000000.0) * 0.30
        else:
            cost = (in_toks / 1000000.0) * 0.15 + (out_toks / 1000000.0) * 0.60
    elif "pro" in model_name.lower():
        if in_toks <= 128000:
            cost = (in_toks / 1000000.0) * 1.25 + (out_toks / 1000000.0) * 5.00
        else:
            cost = (in_toks / 1000000.0) * 2.50 + (out_toks / 1000000.0) * 10.00
            
    # Round to avoid float precision issues, but keep it tight
    if abs(cost - (old_cost or 0)) > 0.000001:
        cursor.execute("UPDATE token_logs SET cost = ? WHERE id = ?", (cost, log_id))
        updated_count += 1

conn.commit()
conn.close()

print(f"Retroactively updated {updated_count} token log records with new cost calculations.")
