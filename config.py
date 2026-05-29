import os

OLLAMA_MODEL = "llama3"
OLLAMA_BASE_URL = "http://localhost:11434"

EMBED_MODEL = "all-MiniLM-L6-v2"

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
TOP_K = 4

CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "data", "chroma")
PLAYER_PROFILE_PATH = os.path.join(os.path.dirname(__file__), "data", "player_profile.json")

WIKI_API_URL = "https://oldschool.runescape.wiki/api.php"
# Items is huge (30k+ pages). Cap per category so ingestion finishes in minutes.
# Quests (~180) and Transportation (~200) are small enough to ingest fully.
WIKI_CATEGORIES = ["Items", "Quests", "Transportation"]
MAX_PAGES_PER_CATEGORY = {"Items": 500, "Quests": 9999, "Transportation": 9999}

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
