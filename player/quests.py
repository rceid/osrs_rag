"""Fetch quest completions from the Runemetrics API."""
import requests

RUNEMETRICS_URL = "https://apps.runescape.com/runemetrics/quests"


def fetch_quests(username: str) -> dict:
    """
    Returns dict of quest_name -> status string ("COMPLETED"/"STARTED"/"NOT_STARTED").
    Raises requests.HTTPError on HTTP failure, ValueError if profile is private.
    """
    resp = requests.get(
        RUNEMETRICS_URL,
        params={"user": username},
        headers={"User-Agent": "osrs-rag-bot/1.0"},
        timeout=10,
    )
    resp.raise_for_status()

    data = resp.json()
    if "error" in data:
        raise ValueError(data.get("error", "Profile may be private or username not found"))

    quests = {}
    for quest in data.get("quests", []):
        quests[quest["title"]] = quest["status"]

    return quests
