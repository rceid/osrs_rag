"""Incrementally add specific categories to the existing Chroma collection.
Skips pages whose title is already present so a full re-scrape isn't needed.

Usage:
    python -m ingestion.add_categories Mechanics Combat
"""
import sys
from tqdm import tqdm

from ingestion.scraper import fetch_category_members, fetch_page_content
from ingestion.chunker import chunk_all
from ingestion.embedder import get_collection, embed_and_store


def add_categories(categories: list[str]) -> None:
    collection = get_collection()

    existing_titles = set()
    res = collection.get(include=["metadatas"])
    for meta in res["metadatas"]:
        if meta and meta.get("title"):
            existing_titles.add(meta["title"])
    print(f"Existing collection: {collection.count()} chunks across {len(existing_titles)} unique pages")

    print("\nEnumerating category members...")
    category_titles: dict[str, list[str]] = {}
    new_total = 0
    for cat in categories:
        members = fetch_category_members(cat)
        titles = [m["title"] for m in members if m["title"] not in existing_titles]
        existing_titles.update(titles)
        category_titles[cat] = titles
        new_total += len(titles)
        print(f"  {cat}: {len(members)} total, {len(titles)} new")

    if new_total == 0:
        print("\nNothing new to add. Done.")
        return

    print(f"\nFetching {new_total} new pages...\n")
    new_pages = []
    with tqdm(total=new_total, unit="pg", smoothing=0.05,
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
        for cat, titles in category_titles.items():
            pbar.set_description(cat[:24])
            pages = fetch_page_content(titles, progress=pbar)
            for p in pages:
                p["category"] = cat.lower()
            new_pages.extend(pages)

    print(f"\nScraped {len(new_pages)} pages with content")
    print("Chunking...")
    chunks = chunk_all(new_pages)
    print(f"Created {len(chunks)} chunks")

    print("\nEmbedding and storing...")
    embed_and_store(chunks, collection)
    print(f"\nDone. Collection now: {collection.count()} chunks")


if __name__ == "__main__":
    cats = sys.argv[1:] or ["Mechanics", "Combat"]
    add_categories(cats)
