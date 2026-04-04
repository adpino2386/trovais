import os
import cohere
from dotenv import load_dotenv
from typing import List

load_dotenv()

co = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
RERANK_MODEL = "rerank-english-v3.0"
TOP_N = 3


def rerank(question: str, results: List[dict], top_n: int = TOP_N) -> List[dict]:
    if not results:
        return []

    documents = [r["content"] for r in results]

    response = co.rerank(
        model=RERANK_MODEL,
        query=question,
        documents=documents,
        top_n=top_n
    )

    reranked = []
    for item in response.results:
        original = results[item.index]
        reranked.append({
            "id": original["id"],
            "content": original["content"],
            "metadata": original["metadata"],
            "similarity": original["similarity"],
            "rerank_score": round(item.relevance_score, 4)
        })

    return reranked