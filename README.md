# OSRS RAG Assistant

A retrieval-augmented chatbot for Old School RuneScape. It scrapes the [OSRS Wiki](https://oldschool.runescape.wiki), embeds the pages into a local [Chroma](https://www.trychroma.com/) vector database, and answers questions through a Streamlit chat UI — grounded in actual wiki content, with sources cited.

Supports player personalization: load your hiscores stats and check off the teleport items you own, and route/travel answers are built around what's actually available to you.

## Requirements

- Python 3.9+
- A free [Mistral AI](https://mistral.ai) API key (see step 3)
- ~500 MB disk for the vector database and embedding model

## Setup

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/rceid/osrs_rag.git
cd osrs_rag
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get a Mistral API key (free)

1. Sign up at [console.mistral.ai](https://console.mistral.ai)
2. Choose the free **Experiment** plan (phone verification required, no credit card)
3. Create an API key under **API Keys**
4. Save it in a `.env` file at the repo root:

```bash
echo 'MISTRAL_API_KEY=your_key_here' > .env
```

The app loads `.env` automatically. The file is gitignored — never commit your key.

> **Note:** The free tier is rate-limited (~1 request/second). Each chat message makes two LLM calls (query rewriting + answering), so rapid-fire questions may briefly hit a 429 error.
>
> **Alternative:** to run fully local with [Ollama](https://ollama.com) instead, set `LLM_PROVIDER = "ollama"` in `config.py`, then `ollama pull llama3` and keep `ollama serve` running. Expect noticeably lower answer quality than Mistral.

### 4. Ingest the wiki (one-time, ~1 hour)

```bash
python -m ingestion.embedder
```

This scrapes ~4,300 pages across categories (weapons, armour, locations, quests, transportation, food, potions, mechanics, …), chunks them, embeds them with `all-MiniLM-L6-v2`, and stores everything in `data/chroma/`. A progress bar shows elapsed time and ETA.

To add more categories later without re-scraping everything:

```bash
python -m ingestion.add_categories "Category name" "Another category"
```

### 5. Run the app

```bash
streamlit run app.py
```

Opens at [http://localhost:8501](http://localhost:8501).

## Using the app

- **Chat** — ask anything: *"What's the fastest way to get to Catherby?"*, *"What does a game tick mean?"*, *"What are the requirements for Lunar Diplomacy?"*
- **Player profile (sidebar)** — enter your OSRS username and click **Load** to pull your stats from the official hiscores (your profile must be set to public in-game)
- **Teleport methods (sidebar)** — check off the teleport items you own; travel answers will prioritize routes using them, listing other methods separately
- **Sources** — every answer includes an expandable list of the wiki pages it drew from

## Project layout

```
config.py            # categories to scrape, models, paths, tunables
ingestion/
  scraper.py         # MediaWiki API client (category listing + page extracts)
  chunker.py         # splits pages into overlapping chunks
  embedder.py        # full ingest: scrape → chunk → embed → store
  add_categories.py  # incremental ingest for new categories
retrieval/
  search.py          # multi-query retrieval against Chroma
chat/
  chain.py           # prompt assembly + chat orchestration
player/
  hiscores.py        # official OSRS hiscores client
  profile.py         # player profile persistence
llm.py               # LLM provider abstraction (Mistral / Ollama)
app.py               # Streamlit UI
```

## Known limitations

- **Quest completion tracking doesn't work** — the Runemetrics quest API is RS3-only; OSRS has no public quest API. Stats load fine; quests stay empty.
- Wiki content is a snapshot from ingestion time; re-run ingestion to refresh.
- The free Mistral tier is rate-limited; heavy use may require the paid tier or switching to Ollama.
