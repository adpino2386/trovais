import psycopg2
from dotenv import load_dotenv
import os
from ingestion.embedder import ingest_file

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
    DELETE FROM documents 
    WHERE metadata->>'filename' = 'nespreso vertuo.pdf'
""")
deleted = cur.rowcount
conn.commit()
cur.close()
conn.close()
print(f"Deleted {deleted} old chunks")

ingest_file('data/sample_manuals/nespreso vertuo.pdf')