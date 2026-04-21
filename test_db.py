import psycopg2

urls = [
    "postgresql://postgres.gustrbzyqrsgfmetayqv:smf3vT3TBBqBoxp5@aws-0-us-west-1.pooler.supabase.com:6543/postgres",
    "postgresql://postgres.gustrbzyqrsgfmetayqv:smf3vT3TBBqBoxp5@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
    "postgresql://postgres:smf3vT3TBBqBoxp5@db.gustrbzyqrsgfmetayqv.supabase.co:6543/postgres"
]

for url in urls:
    print(f"Trying {url} ...")
    try:
        conn = psycopg2.connect(url, connect_timeout=3)
        print("SUCCESS!")
        break
    except Exception as e:
        print(f"FAILED: {e}")
