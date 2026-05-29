"""Read/write player_profile.json."""
import json
import os
from datetime import datetime

from config import PLAYER_PROFILE_PATH

_EMPTY = {
    "username": "",
    "stats": {},
    "quests": {},
    "teleports": [],
    "last_synced": None,
}


def load() -> dict:
    if not os.path.exists(PLAYER_PROFILE_PATH):
        return dict(_EMPTY)
    with open(PLAYER_PROFILE_PATH) as f:
        return json.load(f)


def save(profile: dict) -> None:
    os.makedirs(os.path.dirname(PLAYER_PROFILE_PATH), exist_ok=True)
    with open(PLAYER_PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)


def update_teleports(profile: dict, teleport_keys: list[str]) -> dict:
    profile["teleports"] = teleport_keys
    save(profile)
    return profile


def update_from_api(profile: dict, stats: dict, quests: dict) -> dict:
    profile["stats"] = stats
    profile["quests"] = quests
    profile["last_synced"] = datetime.utcnow().isoformat()
    save(profile)
    return profile
