from typing import List

CHUNK_PROFILES = {
    "short":  {"chunk_size": 60, "overlap": 10},
    "medium": {"chunk_size": 512, "overlap": 50},
    "large":  {"chunk_size": 768, "overlap": 80},
}

def detect_profile(document: dict) -> str:
    all_text = " ".join(p["text"] for p in document["pages"])
    total_pages = max(document.get("total_pages", 1), 1)
    avg_words_per_page = len(all_text.split()) / total_pages

    print(f"  Avg words/page: {avg_words_per_page:.0f}")

    if avg_words_per_page < 150:
        return "short"
    elif avg_words_per_page < 350:
        return "medium"
    else:
        return "large"


def chunk_document(document: dict) -> List[dict]:
    profile_name = detect_profile(document)
    profile = CHUNK_PROFILES[profile_name]
    chunk_size = profile["chunk_size"]
    overlap = profile["overlap"]

    print(f"  Profile: {profile_name} "
          f"(chunk_size={chunk_size}, overlap={overlap})")

    if profile_name == "short":
        return _chunk_full_document(document, chunk_size, overlap)
    else:
        return _chunk_by_page(document, chunk_size, overlap)


def _chunk_full_document(
    document: dict,
    chunk_size: int,
    overlap: int
) -> List[dict]:
    all_text = " ".join(p["text"] for p in document["pages"])
    words = all_text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        if len(chunk_text.strip()) > 30:
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "filename": document["filename"],
                    "filepath": document["filepath"],
                    "page": _estimate_page(start, words, document),
                    "chunk_index": len(chunks),
                    "doc_type": document["type"],
                    "word_count": len(chunk_words)
                }
            })
        start += chunk_size - overlap

    return chunks


def _estimate_page(
    word_index: int,
    all_words: list,
    document: dict
) -> int:
    progress = word_index / max(len(all_words), 1)
    total_pages = document.get("total_pages", 1)
    return max(1, round(progress * total_pages))


def _chunk_by_page(
    document: dict,
    chunk_size: int,
    overlap: int
) -> List[dict]:
    chunks = []
    for page in document["pages"]:
        page_chunks = _chunk_text(
            text=page["text"],
            page_num=page["page"],
            filename=document["filename"],
            filepath=document["filepath"],
            doc_type=document["type"],
            chunk_size=chunk_size,
            overlap=overlap
        )
        chunks.extend(page_chunks)
    return chunks


def _chunk_text(
    text: str,
    page_num: int,
    filename: str,
    filepath: str,
    doc_type: str,
    chunk_size: int,
    overlap: int
) -> List[dict]:
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        if len(chunk_text.strip()) > 50:
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "filename": filename,
                    "filepath": filepath,
                    "page": page_num,
                    "chunk_index": len(chunks),
                    "doc_type": doc_type,
                    "word_count": len(chunk_words)
                }
            })
        start += chunk_size - overlap

    return chunks


def chunk_documents(documents: List[dict]) -> List[dict]:
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"{doc['filename']}: {len(chunks)} chunks")
    print(f"Total chunks: {len(all_chunks)}")
    return all_chunks