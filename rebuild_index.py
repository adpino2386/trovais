import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

print("Dropping old index...")
cur.execute("DROP INDEX IF EXISTS documents_embedding_idx;")

print("Creating HNSW index (memory efficient)...")
cur.execute("""
    CREATE INDEX documents_embedding_idx
    ON documents
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 8, ef_construction = 32);
""")

conn.commit()
cur.close()
conn.close()
print("Index rebuilt successfully!")