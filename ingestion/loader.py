import os
from pathlib import Path
import fitz  # PyMuPDF
from docx import Document as DocxDocument


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def load_document(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    if path.suffix.lower() == ".pdf":
        return _load_pdf(path)
    elif path.suffix.lower() == ".docx":
        return _load_docx(path)
    elif path.suffix.lower() == ".txt":
        return _load_txt(path)


def _load_pdf(path: Path) -> dict:
    doc = fitz.open(str(path))
    pages = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if text:
            pages.append({
                "page": page_num,
                "text": text
            })

    doc.close()

    return {
        "filename": path.name,
        "filepath": str(path),
        "type": "pdf",
        "total_pages": len(pages),
        "pages": pages
    }


def _load_docx(path: Path) -> dict:
    doc = DocxDocument(str(path))
    paragraphs = []

    for i, para in enumerate(doc.paragraphs, start=1):
        text = para.text.strip()
        if text:
            paragraphs.append({
                "page": i,
                "text": text
            })

    return {
        "filename": path.name,
        "filepath": str(path),
        "type": "docx",
        "total_pages": len(paragraphs),
        "pages": paragraphs
    }


def _load_txt(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    return {
        "filename": path.name,
        "filepath": str(path),
        "type": "txt",
        "total_pages": 1,
        "pages": [{"page": 1, "text": text}]
    }


def load_directory(directory: str) -> list[dict]:
    dir_path = Path(directory)

    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    documents = []
    for file_path in dir_path.rglob("*"):
        if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            try:
                print(f"Loading: {file_path.name}")
                doc = load_document(str(file_path))
                documents.append(doc)
            except Exception as e:
                print(f"Failed to load {file_path.name}: {e}")

    print(f"Loaded {len(documents)} documents")
    return documents