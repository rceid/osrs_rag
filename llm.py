"""Single place all LLM calls go through. Provider switched via config.LLM_PROVIDER."""
import requests

from config import (
    LLM_PROVIDER,
    MISTRAL_API_KEY,
    MISTRAL_API_URL,
    MISTRAL_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)


def chat_completion(messages: list[dict], json_mode: bool = False, timeout: int = 120) -> str:
    """Send a chat-format message list, return the assistant's reply text."""
    if LLM_PROVIDER == "mistral":
        return _mistral_chat(messages, json_mode=json_mode, timeout=timeout)
    return _ollama_chat(messages, json_mode=json_mode, timeout=timeout)


def _mistral_chat(messages: list[dict], json_mode: bool = False, timeout: int = 120) -> str:
    if not MISTRAL_API_KEY:
        raise RuntimeError(
            "MISTRAL_API_KEY is not set. Get a free key at console.mistral.ai, then:\n"
            "  export MISTRAL_API_KEY=your_key_here"
        )
    payload = {
        "model": MISTRAL_MODEL,
        "messages": messages,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    resp = requests.post(
        MISTRAL_API_URL,
        json=payload,
        headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _ollama_chat(messages: list[dict], json_mode: bool = False, timeout: int = 120) -> str:
    payload = {"model": OLLAMA_MODEL, "messages": messages, "stream": False}
    if json_mode:
        payload["format"] = "json"
    resp = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()["message"]["content"]
