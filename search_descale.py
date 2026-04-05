# search_descale.py
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
    AND LOWER(content) LIKE '%descal%'
""")

rows = cur.fetchall()
print(f"Chunks containing 'descal': {len(rows)}\n")
for content, page in rows:
    print(f"Page {page}: {content}\n")

cur.close()
conn.close()