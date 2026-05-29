"""Embeds chunks and stores them in Chroma."""
import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_PERSIST_DIR, EMBED_MODEL
from ingestion.scraper import scrape_all
from ingestion.chunker import chunk_all

COLLECTION_NAME = "osrs_wiki"
BATCH_SIZE = 100


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def embed_and_store(chunks: list[dict], collection) -> None:
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        ids = [f"{c['metadata']['title']}_{c['metadata']['chunk_index']}" for c in batch]
        documents = [c["text"] for c in batch]
        metadatas = [c["metadata"] for c in batch]
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        print(f"  Stored chunks {i} – {i + len(batch)}")


def run_ingestion():
    print("Scraping OSRS Wiki...")
    pages = scrape_all()
    print(f"Scraped {len(pages)} pages\n")

    print("Chunking pages...")
    chunks = chunk_all(pages)
    print(f"Created {len(chunks)} chunks\n")

    print("Embedding and storing in Chroma...")
    collection = get_collection()
    embed_and_store(chunks, collection)

    print(f"\nIngestion complete. {collection.count()} chunks stored in Chroma.")


if __name__ == "__main__":
    run_ingestion()
