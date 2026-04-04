import os
import hashlib
import json
import psycopg2
from openai import OpenAI
from dotenv import load_dotenv
from typing import List
from ingestion.chunker import chunk_document
from ingestion.loader import load_document, load_directory

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def compute_file_hash(filepath: str) -> str:
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def is_file_already_ingested(conn, filepath: str, file_hash: str) -> bool:
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM documents 
        WHERE metadata->>'filepath' = %s 
        AND metadata->>'file_hash' = %s
        LIMIT 1
    """, (filepath, file_hash))
    result = cur.fetchone()
    cur.close()
    return result is not None


def delete_file_chunks(conn, filepath: str):
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM documents 
        WHERE metadata->>'filepath' = %s
    """, (filepath,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    print(f"Deleted {deleted} old chunks for: {filepath}")


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
        print(f"Embedded batch {i // BATCH_SIZE + 1} "
              f"({len(batch)} chunks)")
    return all_embeddings


def store_chunks(conn, chunks: List[dict], embeddings: List[List[float]]):
    cur = conn.cursor()
    for chunk, embedding in zip(chunks, embeddings):
        cur.execute("""
            INSERT INTO documents (content, metadata, embedding)
            VALUES (%s, %s, %s)
        """, (
            chunk["text"],
            json.dumps(chunk["metadata"]),
            embedding
        ))
    conn.commit()
    cur.close()


def ingest_file(filepath: str):
    conn = get_connection()
    file_hash = compute_file_hash(filepath)

    if is_file_already_ingested(conn, filepath, file_hash):
        print(f"Skipping (unchanged): {filepath}")
        conn.close()
        return

    delete_file_chunks(conn, filepath)

    print(f"Loading: {filepath}")
    document = load_document(filepath)

    print(f"Chunking: {document['filename']}")
    chunks = chunk_document(document)

    for chunk in chunks:
        chunk["metadata"]["file_hash"] = file_hash

    print(f"Generating embeddings for {len(chunks)} chunks...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = generate_embeddings(texts)

    print(f"Storing in Supabase...")
    store_chunks(conn, chunks, embeddings)

    conn.close()
    print(f"Done: {document['filename']} "
          f"({len(chunks)} chunks ingested)")


def ingest_directory(directory: str):
    from pathlib import Path
    supported = {".pdf", ".docx", ".txt"}
    files = [
        str(p) for p in Path(directory).rglob("*")
        if p.suffix.lower() in supported
    ]

    print(f"Found {len(files)} files in {directory}")
    for filepath in files:
        ingest_file(filepath)

    print(f"\nIngestion complete!")