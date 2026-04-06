# reset_and_reingest.py
from ingestion.embedder import get_connection, ingest_directory
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = get_connection()
cur = conn.cursor()
cur.execute("DELETE FROM documents")
conn.commit()
cur.close()
conn.close()
print("Cleared all chunks from database")

ingest_directory("data/sample_manuals")