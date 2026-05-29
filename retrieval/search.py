"""Query Chroma for relevant wiki chunks."""
import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_PERSIST_DIR, EMBED_MODEL, TOP_K
from ingestion.embedder import COLLECTION_NAME

_collection = None


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
        _collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=ef,
        )
    return _collection


def search(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Return top_k relevant chunks for the query.
    Each result: {"text": ..., "title": ..., "url": ..., "category": ..., "distance": ...}
    """
    collection = _get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": doc,
            "title": meta.get("title", ""),
            "url": meta.get("url", ""),
            "category": meta.get("category", ""),
            "distance": dist,
        })

    return chunks
