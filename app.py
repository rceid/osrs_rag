"""OSRS RAG Chatbot — Streamlit UI."""
import streamlit as st

from config import TELEPORT_ITEMS
from player import profile as profile_store
from player.hiscores import fetch_stats
from player.quests import fetch_quests
from chat.chain import chat

st.set_page_config(page_title="OSRS Assistant", page_icon="⚔️", layout="wide")

# ── Session state init ────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

if "profile" not in st.session_state:
    st.session_state.profile = profile_store.load()


def _sync_player(username: str):
    with st.spinner(f"Loading {username}..."):
        try:
            stats = fetch_stats(username)
            quests = fetch_quests(username)
            st.session_state.profile["username"] = username
            profile_store.update_from_api(st.session_state.profile, stats, quests)
            st.success(f"Loaded {username}: {len(stats)} skills, {len(quests)} quests")
        except Exception as e:
            st.error(f"Could not load profile: {e}")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Player Profile")

    col1, col2 = st.columns([3, 1])
    with col1:
        username_input = st.text_input(
            "OSRS Username",
            value=st.session_state.profile.get("username", ""),
            label_visibility="collapsed",
            placeholder="OSRS Username",
        )
    with col2:
        if st.button("Load"):
            if username_input.strip():
                _sync_player(username_input.strip())
            else:
                st.warning("Enter a username")

    if st.session_state.profile.get("username"):
        st.caption(
            f"⚠️ Profile must be set to **Public** in your OSRS account settings."
        )
        if st.session_state.profile.get("last_synced"):
            st.caption(f"Last synced: {st.session_state.profile['last_synced'][:19].replace('T', ' ')} UTC")
        if st.button("Refresh", use_container_width=True):
            _sync_player(st.session_state.profile["username"])

    # Stats display
    stats = st.session_state.profile.get("stats", {})
    if stats:
        st.subheader("Stats")
        STAT_COLS = [
            ("attack", "strength", "defence"),
            ("hitpoints", "prayer", "magic"),
            ("ranged", "mining", "smithing"),
            ("fishing", "cooking", "woodcutting"),
            ("agility", "herblore", "thieving"),
            ("crafting", "fletching", "slayer"),
            ("farming", "runecraft", "hunter"),
            ("construction", "firemaking", None),
        ]
        for row in STAT_COLS:
            cols = st.columns(3)
            for col, skill in zip(cols, row):
                if skill and skill in stats:
                    col.metric(skill.capitalize(), stats[skill])

    st.divider()

    # Teleport checkboxes
    st.subheader("Teleport Methods")
    current_teleports = set(st.session_state.profile.get("teleports", []))
    new_teleports = []
    for key, label in TELEPORT_ITEMS:
        checked = st.checkbox(label, value=key in current_teleports, key=f"tp_{key}")
        if checked:
            new_teleports.append(key)

    if set(new_teleports) != current_teleports:
        profile_store.update_teleports(st.session_state.profile, new_teleports)
        st.session_state.profile["teleports"] = new_teleports


# ── Main chat area ─────────────────────────────────────────────────────────────
st.title("⚔️ OSRS Assistant")

if not st.session_state.history:
    st.info(
        "Ask me anything about OSRS — quests, items, transportation, skilling, "
        "or the fastest way to get somewhere. Load your player profile in the "
        "sidebar so I can tailor answers to your stats and available teleports."
    )

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("Sources"):
                for src in msg["sources"]:
                    st.markdown(f"- [{src['title']}]({src['url']})")

user_input = st.chat_input("Ask a question about OSRS...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer, new_history, sources = chat(
                    user_input,
                    [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.history
                    ],
                    st.session_state.profile if st.session_state.profile.get("username") else None,
                )
                st.markdown(answer)
                if sources:
                    with st.expander("Sources"):
                        seen_urls = set()
                        for src in sources:
                            if src["url"] not in seen_urls:
                                st.markdown(f"- [{src['title']}]({src['url']})")
                                seen_urls.add(src["url"])

                st.session_state.history = [
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.history],
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": answer, "sources": sources},
                ]
            except Exception as e:
                st.error(f"Error: {e}")
                if "Connection refused" in str(e) or "11434" in str(e):
                    st.info("Make sure Ollama is running: `ollama serve` in a terminal")
