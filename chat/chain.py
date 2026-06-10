"""Builds prompts, manages chat history, and calls the configured LLM."""
from __future__ import annotations

from llm import chat_completion
from retrieval.search import search


SYSTEM_PROMPT = """You are a knowledgeable OSRS (Old School RuneScape) assistant.

CRITICAL RULES — these prevent giving wrong information:
1. ONLY use facts that appear in the "Relevant wiki information" below. If a fact is not in the context, you do NOT know it.
2. If the user asks for specific details (quest requirements, item stats, levels, exact codes, prices) and those details are NOT in the context, say so explicitly: "I don't see the specific requirements in the wiki excerpts I have — check the wiki page directly." DO NOT GUESS, ESTIMATE, OR MAKE UP NUMBERS OR REQUIREMENTS.
3. When asked about travel/transport to a location, consider ALL methods in the context — including teleport spells, jewellery teleports, fairy ring codes (e.g. "DHY"), spirit trees, and amulets — and list them comparatively (fastest first). Don't fixate on the first method you see.
4. When recommending routes, only suggest options the player has available based on their stats and teleport items in the player profile.
5. Always cite sources by referencing wiki page titles in brackets, e.g. [Fairy rings].

Be specific and helpful, but honesty about gaps beats confident guessing."""

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

    answer = chat_completion(messages)

    updated_history = history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": answer},
    ]

    return answer, updated_history, chunks
