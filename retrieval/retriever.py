import os
import json
import psycopg2
from openai import OpenAI
from dotenv import load_dotenv
from typing import List

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBEDDING_MODEL = "text-embedding-3-small"
TOP_K = 5


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def embed_question(question: str) -> List[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=question
    )
    return response.data[0].embedding


def retrieve(question: str, top_k: int = TOP_K) -> List[dict]:
    embedding = embed_question(question)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            content,
            metadata,
            1 - (embedding <=> %s::vector) AS similarity
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (embedding, embedding, top_k))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    results = []
    for row in rows:
        doc_id, content, metadata, similarity = row
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        results.append({
            "id": doc_id,
            "content": content,
            "metadata": metadata,
            "similarity": round(similarity, 4)
        })

    return results


def format_results(results: List[dict]) -> str:
    output = []
    for i, r in enumerate(results, 1):
        filename = r["metadata"].get("filename", "unknown")
        page = r["metadata"].get("page", "?")
        similarity = r["similarity"]
        output.append(
            f"[{i}] {filename} — page {page} "
            f"(similarity: {similarity})\n{r['content'][:300]}..."
        )
    return "\n\n".join(output)