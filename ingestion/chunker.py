from typing import List


CHUNK_SIZE = 512
CHUNK_OVERLAP = 50


def chunk_document(document: dict) -> List[dict]:
    chunks = []

    for page in document["pages"]:
        page_chunks = _chunk_text(
            text=page["text"],
            page_num=page["page"],
            filename=document["filename"],
            filepath=document["filepath"],
            doc_type=document["type"]
        )
        chunks.extend(page_chunks)

    return chunks


def _chunk_text(
    text: str,
    page_num: int,
    filename: str,
    filepath: str,
    doc_type: str
) -> List[dict]:
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + CHUNK_SIZE
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

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def chunk_documents(documents: List[dict]) -> List[dict]:
    all_chunks = []

    for doc in documents:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"{doc['filename']}: {len(chunks)} chunks")

    print(f"Total chunks: {len(all_chunks)}")
    return all_chunks