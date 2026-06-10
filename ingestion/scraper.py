"""Fetches OSRS Wiki pages via the MediaWiki API."""
import time
import requests
from tqdm import tqdm
from config import WIKI_API_URL, WIKI_CATEGORIES, MAX_PAGES_PER_CATEGORY as _MAX

# Be a good API citizen — don't hammer the wiki
REQUEST_DELAY = 0.5
PAGES_PER_REQUEST = 50
# extracts API allows max 20 pages per batch (exlimit cap)
EXTRACT_BATCH_SIZE = 20


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


def fetch_page_content(titles: list[str], progress=None) -> list[dict]:
    """Return list of {title, content, url} for each title (batched 50 at a time)."""
    pages = []
    session = requests.Session()
    session.headers.update({"User-Agent": "osrs-rag-bot/1.0 (learning project)"})

    for i in range(0, len(titles), EXTRACT_BATCH_SIZE):
        batch = titles[i : i + EXTRACT_BATCH_SIZE]
        base_params = {
            "action": "query",
            "titles": "|".join(batch),
            "prop": "extracts|info",
            "explaintext": True,
            "exsectionformat": "plain",
            "exlimit": EXTRACT_BATCH_SIZE,
            "inprop": "url",
            "format": "json",
        }
        # MediaWiki's extracts API only returns one extract per request even with
        # exlimit set; follow excontinue to collect the rest within this batch.
        params = dict(base_params)
        collected = {}
        while True:
            resp = session.get(WIKI_API_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            for page in data["query"]["pages"].values():
                title = page.get("title")
                extract = page.get("extract", "")
                if not extract or not extract.strip() or title in collected:
                    continue
                collected[title] = {
                    "title": title,
                    "content": extract,
                    "url": page.get("fullurl", f"https://oldschool.runescape.wiki/w/{title.replace(' ', '_')}"),
                }
            if "continue" not in data:
                break
            params = dict(base_params)
            params.update(data["continue"])
            time.sleep(REQUEST_DELAY)

        pages.extend(collected.values())
        if progress is not None:
            progress.update(len(batch))
        time.sleep(REQUEST_DELAY)

    return pages


def scrape_all() -> list[dict]:
    """Scrape all pages across configured categories. Returns list of page dicts."""
    all_pages = []
    seen_titles = set()

    # Phase 1: enumerate all category members up-front so the progress bar has a total
    print("Enumerating category members...")
    category_titles: dict[str, list[str]] = {}
    for category in WIKI_CATEGORIES:
        members = fetch_category_members(category)
        limit = _MAX if isinstance(_MAX, int) else _MAX.get(category, 400)
        titles = [m["title"] for m in members if m["title"] not in seen_titles][:limit]
        seen_titles.update(titles)
        category_titles[category] = titles
        print(f"  {category}: {len(titles)} pages")

    total_pages = sum(len(t) for t in category_titles.values())
    print(f"\nTotal unique pages to fetch: {total_pages}\n")

    # Phase 2: fetch content with a single global progress bar (shows elapsed + ETA + pages/sec)
    with tqdm(total=total_pages, unit="pg", smoothing=0.05,
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
        for category, titles in category_titles.items():
            pbar.set_description(category[:24])
            pages = fetch_page_content(titles, progress=pbar)
            for page in pages:
                page["category"] = category.lower()
            all_pages.extend(pages)

    return all_pages


if __name__ == "__main__":
    pages = scrape_all()
    print(f"\nTotal pages scraped: {len(pages)}")
