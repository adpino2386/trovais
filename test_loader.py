from retrieval.retriever import retrieve, format_results

question = "Any exercises related to palingrams?"  # Example question to test retrieval
print(f"Question: {question}\n")

results = retrieve(question)
print(format_results(results))