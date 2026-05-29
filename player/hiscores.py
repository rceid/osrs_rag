"""Fetch player stats from the OSRS Hiscores API."""
import requests
from config import SKILLS

HISCORES_URL = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws"


def fetch_stats(username: str) -> dict:
    """
    Returns dict of skill_name -> level, e.g. {"attack": 80, "strength": 85, ...}.
    Raises requests.HTTPError on failure, ValueError if response is unexpected.
    """
    resp = requests.get(
        HISCORES_URL,
        params={"player": username},
        headers={"User-Agent": "osrs-rag-bot/1.0"},
        timeout=10,
    )
    resp.raise_for_status()

    lines = resp.text.strip().split("\n")
    stats = {}

    # Hiscores returns one line per skill: rank,level,xp
    for i, skill in enumerate(SKILLS):
        if i >= len(lines):
            break
        parts = lines[i].split(",")
        if len(parts) >= 2:
            try:
                level = int(parts[1])
                if level > 0:
                    stats[skill] = level
            except ValueError:
                pass

    return stats
