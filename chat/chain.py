"""Builds prompts, manages chat history, and calls Ollama."""
import requests
import json

from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from retrieval.search import search


SYSTEM_PROMPT = """You are a knowledgeable OSRS (Old School RuneScape) assistant.
Answer questions using the wiki context provided. Be specific and helpful.
When recommending routes or methods, only suggest options the player has available based on their stats and teleport items.
Always cite your sources by referencing the wiki page titles."""

MAX_HISTORY = 10


def _build_context_block(chunks: list[dict]) -> str:
    lines = []
    for i, chunk in enumerate(chunks, 1):
        lines.append(f"[Source {i}: {chunk['title']}]\n{chunk['text']}")
    return "\n\n".join(lines)


def _build_player_context(profile: dict | None) -> str:
    if not profile:
        return ""

    lines = ["Player profile:"]

    if profile.get("username"):
        lines.append(f"- Username: {profile['username']}")

    if profile.get("stats"):
        stats_str = ", ".join(
            f"{k.capitalize()} {v}"
            for k, v in profile["stats"].items()
            if v and v > 1
        )
        if stats_str:
            lines.append(f"- Stats: {stats_str}")

    if profile.get("quests"):
        completed = [q for q, s in profile["quests"].items() if s == "COMPLETED"]
        if completed:
            lines.append(f"- Completed quests: {', '.join(completed[:20])}")
            if len(completed) > 20:
                lines.append(f"  (and {len(completed) - 20} more)")

    if profile.get("teleports"):
        lines.append(f"- Available teleports: {', '.join(profile['teleports'])}")

    return "\n".join(lines)


def chat(
    user_message: str,
    history: list[dict],
    player_profile: dict | None = None,
) -> tuple[str, list[dict], list[dict]]:
    """
    Send a message and return (answer, updated_history, source_chunks).
    history is a list of {"role": "user"|"assistant", "content": "..."}.
    """
    chunks = search(user_message)

    player_ctx = _build_player_context(player_profile)
    wiki_ctx = _build_context_block(chunks)

    system = SYSTEM_PROMPT
    if player_ctx:
        system += f"\n\n{player_ctx}"
    if wiki_ctx:
        system += f"\n\nRelevant wiki information:\n{wiki_ctx}"

    messages = [{"role": "system", "content": system}]
    messages.extend(history[-MAX_HISTORY:])
    messages.append({"role": "user", "content": user_message})

    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
        timeout=120,
    )
    resp.raise_for_status()
    answer = resp.json()["message"]["content"]

    updated_history = history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": answer},
    ]

    return answer, updated_history, chunks
