import streamlit as st
import requests

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Chat · SupplyCode.pdf",
    page_icon="⚡",
    layout="centered",
)

API_URL = "http://localhost:8000"

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"|"assistant", "content": str}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    api_url = st.text_input("API Base URL", value=API_URL)

    st.divider()

    mode = st.radio(
        "Mode",
        options=["💬 Chat (streaming)", "🔍 Search chunks"],
    )

    st.divider()

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("RAG Chat · SupplyCode.pdf")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("⚡ RAG Chat")
st.caption("Retrieval-Augmented Generation · SupplyCode.pdf")
st.divider()

# ── Chat history ──────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.info("🔍 Ask anything about your document to get started.", icon="💡")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ── Input area ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask a question about SupplyCode.pdf…")

# ── Send logic ────────────────────────────────────────────────────────────────
if user_input and user_input.strip():
    query = user_input.strip()

    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    # ── Chat (streaming) mode ─────────────────────────────────────────────
    if mode.startswith("💬"):
        with st.chat_message("assistant"):
            answer_placeholder = st.empty()
            answer = ""
            try:
                with st.spinner("Thinking…"):
                    with requests.post(
                        f"{api_url}/ask",
                        json={"query": query},
                        stream=True,
                        timeout=60,
                    ) as resp:
                        resp.raise_for_status()
                        for chunk in resp.iter_content(chunk_size=None):
                            if chunk:
                                answer += chunk.decode("utf-8", errors="replace")
                                answer_placeholder.write(answer + " ▌")

                answer_placeholder.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except requests.exceptions.ConnectionError:
                msg = f"❌ Cannot reach the API. Is the FastAPI server running on `{api_url}`?"
                answer_placeholder.error(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
            except Exception as e:
                msg = f"❌ Error: {e}"
                answer_placeholder.error(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})

    # ── Search chunks mode ────────────────────────────────────────────────
    else:
        with st.chat_message("assistant"):
            try:
                with st.spinner("Searching…"):
                    resp = requests.post(
                        f"{api_url}/search",
                        json={"query": query},
                        timeout=30,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    context = data.get("context", "No results found.")

                result = f"📄 **Retrieved chunks:**\n\n{context}"
                st.write(result)
                st.session_state.messages.append({"role": "assistant", "content": result})

            except requests.exceptions.ConnectionError:
                msg = f"❌ Cannot reach the API. Is the FastAPI server running on `{api_url}`?"
                st.error(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
            except Exception as e:
                msg = f"❌ Error: {e}"
                st.error(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})