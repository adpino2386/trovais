import os
import anthropic
from dotenv import load_dotenv
from typing import List

load_dotenv()

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """You are Trovais, an expert knowledge assistant. 
Your job is to answer questions accurately using ONLY the context 
provided below. 

Rules you must always follow:
- Only use information from the provided context
- Always cite your sources using [page X, filename] format
- If the context does not contain enough information to answer, 
  say so clearly — never make up an answer
- Be concise and precise
- If the question is in French, answer in French
- If the question is in English, answer in English"""


def build_context(chunks: List[dict]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        filename = chunk["metadata"].get("filename", "unknown")
        page = chunk["metadata"].get("page", "?")
        context_parts.append(
            f"[Source {i}: {filename}, page {page}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(context_parts)


def generate_answer(question: str, chunks: List[dict]) -> dict:
    context = build_context(chunks)

    user_message = f"""Context:
{context}

Question: {question}

Answer based only on the context above, with source citations."""

    response = claude.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    return {
        "answer": response.content[0].text,
        "sources": [
            {
                "filename": c["metadata"].get("filename"),
                "page": c["metadata"].get("page"),
                "rerank_score": c.get("rerank_score", c.get("similarity"))
            }
            for c in chunks
        ],
        "model": MODEL,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens
    }