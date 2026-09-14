import PyPDF2


def extract_text_by_page(file_path: str) -> list[dict]:
    """
    Returns [{ "page": 1, "text": "..." }, ...]
    Keeping page numbers attached here is what lets the Tutor cite
    'Document Name - Page 14' later.
    """
    pages = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append({"page": i + 1, "text": text})
    return pages


def chunk_pages(pages: list[dict], chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Simple fixed-size word-count chunking with overlap.
    Overlap prevents cutting a sentence exactly at a chunk boundary.
    Each chunk keeps its source page number for citations.
    """
    chunks = []
    for p in pages:
        words = p["text"].split()
        if not words:
            continue
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk_text = " ".join(words[start:end])
            chunks.append({"text": chunk_text, "page": p["page"]})
            start += chunk_size - overlap
    return chunks