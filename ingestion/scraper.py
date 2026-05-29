"""Fetches OSRS Wiki pages via the MediaWiki API."""
import time
import requests
from config import WIKI_API_URL, WIKI_CATEGORIES, MAX_PAGES_PER_CATEGORY

# Be a good API citizen — don't hammer the wiki
REQUEST_DELAY = 0.5
PAGES_PER_REQUEST = 50


def fetch_category_members(category: str) -> list[dict]:
    """Return list of {pageid, title} for all pages in a category."""
    members = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": PAGES_PER_REQUEST,
        "cmtype": "page",
        "format": "json",
    }
    session = requests.Session()
    session.headers.update({"User-Agent": "osrs-rag-bot/1.0 (learning project)"})

    while True:
        resp = session.get(WIKI_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        members.extend(data["query"]["categorymembers"])
        if "continue" not in data:
            break
        params["cmcontinue"] = data["continue"]["cmcontinue"]
        time.sleep(REQUEST_DELAY)

    return members


def fetch_page_content(titles: list[str]) -> list[dict]:
    """Return list of {title, content, url} for each title (batched 50 at a time)."""
    pages = []
    session = requests.Session()
    session.headers.update({"User-Agent": "osrs-rag-bot/1.0 (learning project)"})

    for i in range(0, len(titles), 50):
        batch = titles[i : i + 50]
        params = {
            "action": "query",
            "titles": "|".join(batch),
            "prop": "extracts|info",
            "explaintext": True,
            "exsectionformat": "plain",
            "inprop": "url",
            "format": "json",
        }
        resp = session.get(WIKI_API_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        for page in data["query"]["pages"].values():
            if "extract" not in page or not page.get("extract", "").strip():
                continue
            pages.append({
                "title": page["title"],
                "content": page["extract"],
                "url": page.get("fullurl", f"https://oldschool.runescape.wiki/w/{page['title'].replace(' ', '_')}"),
            })

        time.sleep(REQUEST_DELAY)

    return pages


def scrape_all() -> list[dict]:
    """Scrape all pages across configured categories. Returns list of page dicts."""
    all_pages = []
    seen_titles = set()

    for category in WIKI_CATEGORIES:
        print(f"Fetching category: {category}")
        members = fetch_category_members(category)
        limit = MAX_PAGES_PER_CATEGORY.get(category, 500)
        titles = [m["title"] for m in members if m["title"] not in seen_titles][:limit]
        seen_titles.update(titles)
        print(f"  {len(titles)} pages to fetch")

        pages = fetch_page_content(titles)
        for page in pages:
            page["category"] = category.lower()
        all_pages.extend(pages)
        print(f"  {len(pages)} pages fetched with content")

    return all_pages


if __name__ == "__main__":
    pages = scrape_all()
    print(f"\nTotal pages scraped: {len(pages)}")
