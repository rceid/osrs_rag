import os

# Load .env (supports optional "export " prefix); real env vars take precedence
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if not _line or _line.startswith("#"):
                continue
            if _line.startswith("export "):
                _line = _line[len("export "):]
            if "=" in _line:
                _k, _, _v = _line.partition("=")
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

# LLM provider: "mistral" (hosted API, needs MISTRAL_API_KEY env var) or "ollama" (local)
LLM_PROVIDER = "mistral"

MISTRAL_MODEL = "mistral-small-latest"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")

OLLAMA_MODEL = "llama3"
OLLAMA_BASE_URL = "http://localhost:11434"

EMBED_MODEL = "all-MiniLM-L6-v2"

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
TOP_K = 10

CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "data", "chroma")
PLAYER_PROFILE_PATH = os.path.join(os.path.dirname(__file__), "data", "player_profile.json")

WIKI_API_URL = "https://oldschool.runescape.wiki/api.php"
# Target specific subcategories instead of the 30k+ flat Items list.
# Quests (~180 pages) and Transportation are fetched fully.
# Item subcategories are smaller and more useful for Q&A.
WIKI_CATEGORIES = [
    "Weapons",
    "Armour",
    "Jewellery",
    "Equipment",
    "Melee weapons",
    "Spells",
    "Members' spells",
    "Quests",
    "Transportation",
    "Locations",
    "Legs slot items",
    "Shield slot items",
    "Cape slot items",
    "Feet slot items",
    "Potions",
    "Food",
    "Mechanics",
    "Combat",
]
MAX_PAGES_PER_CATEGORY = 1200  # per category, as a safety cap

# Teleport items shown in sidebar
TELEPORT_ITEMS = [
    ("dramen_staff", "Dramen staff (fairy rings)"),
    ("ardougne_cloak_2", "Ardougne cloak 2"),
    ("ardougne_cloak_4", "Ardougne cloak 4"),
    ("games_necklace", "Games necklace"),
    ("amulet_of_glory", "Amulet of glory"),
    ("slayer_ring", "Slayer ring"),
    ("karamja_gloves_3", "Karamja gloves 3"),
    ("ring_of_dueling", "Ring of dueling"),
    ("combat_bracelet", "Combat bracelet"),
    ("skills_necklace", "Skills necklace"),
    ("digsite_pendant", "Digsite pendant"),
    ("necklace_of_passage", "Necklace of passage"),
    ("burning_amulet", "Burning amulet"),
    ("xerics_talisman", "Xeric's talisman"),
    ("construction_cape", "Construction cape"),
    ("max_cape", "Max cape"),
    ("portal_nexus", "Portal nexus (POH)"),
    ("house_tabs", "House teleport tablets"),
]

SKILLS = [
    "attack", "strength", "defence", "ranged", "prayer", "magic",
    "runecraft", "hitpoints", "crafting", "mining", "smithing", "fishing",
    "cooking", "firemaking", "woodcutting", "agility", "herblore",
    "thieving", "fletching", "slayer", "farming", "construction", "hunter",
]
