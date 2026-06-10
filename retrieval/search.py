"""Query Chroma for relevant wiki chunks."""
import json
import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_PERSIST_DIR, EMBED_MODEL, TOP_K
from ingestion.embedder import COLLECTION_NAME
from llm import chat_completion

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


QUERY_REWRITE_PROMPT = """Rewrite this OSRS player question into 3 short, distinct search queries that would find the most useful wiki passages to answer it.
Focus on different angles: the destination/topic itself, related transport/teleport methods, and any prerequisites/requirements.
Return ONLY a JSON array of 3 strings, no prose.

Question: {query}"""


def _generate_query_variants(query: str) -> list[str]:
    """Ask the LLM for 2-3 alternate phrasings of the query. Falls back to [query] on error."""
    try:
        text = chat_completion(
            [{"role": "user", "content": QUERY_REWRITE_PROMPT.format(query=query)}],
            json_mode=True,
            timeout=30,
        ).strip()
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            for v in parsed.values():
                if isinstance(v, list):
                    parsed = v
                    break
        variants = [str(s).strip() for s in parsed if str(s).strip()]
        return variants[:3] if variants else [query]
    except Exception:
        return [query]


def search(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Multi-query retrieval: rewrite the query into variants, search each, union & dedupe.
    Each result: {"text": ..., "title": ..., "url": ..., "category": ..., "distance": ...}
    """
    collection = _get_collection()
    variants = _generate_query_variants(query)
    queries = [query] + [v for v in variants if v != query]

    per_query_k = max(top_k // 2, 4)
    seen_ids = set()
    chunks = []

    results = collection.query(
        query_texts=queries,
        n_results=per_query_k,
        include=["documents", "metadatas", "distances"],
    )

    for i in range(len(queries)):
        for doc_id, doc, meta, dist in zip(
            results["ids"][i],
            results["documents"][i],
            results["metadatas"][i],
            results["distances"][i],
        ):
            if doc_id in seen_ids:
                continue
            seen_ids.add(doc_id)
            chunks.append({
                "text": doc,
                "title": meta.get("title", ""),
                "url": meta.get("url", ""),
                "category": meta.get("category", ""),
                "distance": dist,
            })

    chunks.sort(key=lambda c: c["distance"])
    return chunks[:top_k]
