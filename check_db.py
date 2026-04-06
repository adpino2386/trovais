import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
    SELECT metadata->>'filename', COUNT(*) 
    FROM documents 
    GROUP BY metadata->>'filename'
""")

rows = cur.fetchall()
print("Documents in Supabase:")
for row in rows:
    print(f"  {row[0]}: {row[1]} chunks")

cur.close()
conn.close()