"""Splits wiki page content into overlapping chunks."""
from config import CHUNK_SIZE, CHUNK_OVERLAP


def _tokenize_approx(text: str) -> list[str]:
    # Rough word-based tokenization — ~1.3 words per token on average
    return text.split()


def chunk_page(page: dict) -> list[dict]:
    """
    Split a page into overlapping chunks of ~CHUNK_SIZE tokens.
    Returns list of chunk dicts with text and metadata.
    """
    words = _tokenize_approx(page["content"])
    # Convert token counts to word counts (1 token ≈ 0.75 words)
    words_per_chunk = int(CHUNK_SIZE * 0.75)
    words_overlap = int(CHUNK_OVERLAP * 0.75)

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(words):
        end = min(start + words_per_chunk, len(words))
        chunk_text = " ".join(words[start:end])

        chunks.append({
            "text": chunk_text,
            "metadata": {
                "title": page["title"],
                "url": page["url"],
                "category": page.get("category", "unknown"),
                "chunk_index": chunk_index,
            },
        })

        if end == len(words):
            break

        start += words_per_chunk - words_overlap
        chunk_index += 1

    return chunks


def chunk_all(pages: list[dict]) -> list[dict]:
    all_chunks = []
    for page in pages:
        all_chunks.extend(chunk_page(page))
    return all_chunks
