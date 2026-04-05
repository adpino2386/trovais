import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
    SELECT content, metadata->>'page'
    FROM documents
    WHERE metadata->>'filename' = 'nespreso vertuo.pdf'
    ORDER BY (metadata->>'chunk_index')::int
    LIMIT 20
""")

rows = cur.fetchall()
print(f"Nespresso chunks in database:\n")
for i, (content, page) in enumerate(rows, 1):
    print(f"[{i}] Page {page}: {content[:200]}")
    print()

cur.close()
conn.close()