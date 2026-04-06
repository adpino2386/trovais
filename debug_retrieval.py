from retrieval.retriever import retrieve
from retrieval.reranker import rerank

question = "does the nespresso vertuo coffee machine tell me when to descale? any warning?"

print("=== AFTER RETRIEVAL (top 10) ===\n")
results = retrieve(question, top_k=10)
for i, r in enumerate(results, 1):
    print(f"[{i}] Score: {r['similarity']} | "
          f"File: {r['metadata']['filename']} | "
          f"Page: {r['metadata']['page']}")
    print(f"    Text: {r['content'][:120]}\n")

print("\n=== AFTER RERANKING (top 5) ===\n")
reranked = rerank(question, results, top_n=5)
for i, r in enumerate(reranked, 1):
    print(f"[{i}] Rerank: {r['rerank_score']} | "
          f"File: {r['metadata']['filename']} | "
          f"Page: {r['metadata']['page']}")
    print(f"    Text: {r['content'][:120]}\n")