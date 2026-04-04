from retrieval.retriever import retrieve
from retrieval.reranker import rerank

question = "Any exercises related to palingrams?"
print(f"Question: {question}\n")

print("=== Before reranking ===")
results = retrieve(question)
for i, r in enumerate(results, 1):
    print(f"[{i}] page {r['metadata']['page']} | "
          f"similarity: {r['similarity']} | "
          f"{r['content'][:100]}...")

print("\n=== After reranking ===")
reranked = rerank(question, results)
for i, r in enumerate(reranked, 1):
    print(f"[{i}] page {r['metadata']['page']} | "
          f"rerank score: {r['rerank_score']} | "
          f"{r['content'][:100]}...")