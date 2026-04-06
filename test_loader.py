from retrieval.retriever import retrieve
from retrieval.reranker import rerank
from retrieval.generator import generate_answer

question = "Any exercises related to palingrams?"
print(f"Question: {question}\n")

results = retrieve(question)
reranked = rerank(question, results)
response = generate_answer(question, reranked)

print("=== Answer ===")
print(response["answer"])
print("\n=== Sources ===")
for s in response["sources"]:
    print(f"- {s['filename']} | page {s['page']} | "
          f"score: {s['rerank_score']}")
print(f"\nTokens used: {response['input_tokens']} in, "
      f"{response['output_tokens']} out")