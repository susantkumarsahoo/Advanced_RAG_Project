import streamlit as st
import requests

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Chat",
    page_icon="⚡",
    layout="centered",
)

API_URL = "http://localhost:8000"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
    background-color: #0d0f12 !important;
    color: #e8eaf0 !important;
}

/* Main container */
.block-container {
    max-width: 780px !important;
    padding-top: 2rem !important;
}

/* Header */
.rag-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 16px;
    border-bottom: 1px solid #252a33;
    margin-bottom: 24px;
}
.rag-logo {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #00e5a0, #0099ff);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
}
.rag-title { font-size: 1.25rem; font-weight: 700; letter-spacing: -0.02em; }
.rag-sub   { font-size: 0.72rem; color: #5a6270; font-family: 'JetBrains Mono', monospace; margin-left: auto; }

/* Chat bubbles */
.msg-user, .msg-bot {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 16px;
    animation: fadeUp 0.25s ease both;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.msg-user { align-items: flex-end; }
.msg-bot  { align-items: flex-start; }

.msg-label {
    font-size: 0.68rem;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #5a6270;
}
.msg-label-user { color: #0099ff; }

.bubble {
    max-width: 88%;
    padding: 14px 18px;
    border-radius: 12px;
    line-height: 1.65;
    font-size: 0.92rem;
    white-space: pre-wrap;
    word-break: break-word;
}
.bubble-user {
    background: #1a2535;
    border: 1px solid #1e3050;
    color: #e8eaf0;
    text-align: right;
}
.bubble-bot {
    background: #111815;
    border: 1px solid #252a33;
    color: #e8eaf0;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #5a6270;
    font-size: 0.88rem;
}
.empty-icon { font-size: 2.5rem; margin-bottom: 12px; }

/* Streamlit widget overrides */
.stTextArea textarea {
    background: #161a20 !important;
    border: 1px solid #252a33 !important;
    border-radius: 12px !important;
    color: #e8eaf0 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.92rem !important;
}
.stTextArea textarea:focus {
    border-color: #00e5a0 !important;
    box-shadow: 0 0 0 1px #00e5a0 !important;
}

.stButton > button {
    background: #00e5a0 !important;
    color: #000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.15s, transform 0.1s !important;
    width: 100% !important;
}
.stButton > button:hover {
    opacity: 0.85 !important;
    transform: scale(1.02) !important;
}
.stButton > button:disabled {
    opacity: 0.3 !important;
}

/* Sidebar overrides */
[data-testid="stSidebar"] {
    background: #161a20 !important;
    border-right: 1px solid #252a33 !important;
}
[data-testid="stSidebar"] * {
    color: #e8eaf0 !important;
}

/* Divider */
hr { border-color: #252a33 !important; }

/* Spinner */
.stSpinner > div { border-top-color: #00e5a0 !important; }

/* Selectbox / text_input in sidebar */
.stSelectbox > div, .stTextInput > div > div {
    background: #0d0f12 !important;
    border-color: #252a33 !important;
    color: #e8eaf0 !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []   # list of {"role": "user"|"bot", "text": str}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_url = st.text_input("API Base URL", value=API_URL)
    st.markdown("---")
    st.markdown("**Mode**")
    mode = st.radio("", ["💬 Chat (streaming)", "🔍 Search chunks"], label_visibility="collapsed")
    st.markdown("---")
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown(
        "<span style='font-size:0.72rem;color:#5a6270;font-family:JetBrains Mono,monospace;'>"
        "RAG Chat · SupplyCode.pdf</span>",
        unsafe_allow_html=True
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rag-header">
  <div class="rag-logo">⚡</div>
  <div class="rag-title">RAG Chat</div>
  <div class="rag-sub">SupplyCode.pdf</div>
</div>
""", unsafe_allow_html=True)

# ── Chat history ──────────────────────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">🔍</div>
          <div>Ask anything about your document</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="msg-user">
                  <div class="msg-label msg-label-user">You</div>
                  <div class="bubble bubble-user">{msg["text"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="msg-bot">
                  <div class="msg-label">Assistant</div>
                  <div class="bubble bubble-bot">{msg["text"]}</div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")

# ── Input area ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_area(
        "Query",
        placeholder="Ask a question…",
        label_visibility="collapsed",
        max_chars=1000,
        height=80,
        key="user_input",
    )
with col2:
    send = st.button("➤ Send", use_container_width=True)

st.markdown(
    "<div style='text-align:center;font-size:0.72rem;color:#5a6270;margin-top:6px;'>"
    "Ctrl+Enter to send in most browsers</div>",
    unsafe_allow_html=True
)

# ── Send logic ────────────────────────────────────────────────────────────────
if send and user_input.strip():
    query = user_input.strip()
    st.session_state.messages.append({"role": "user", "text": query})

    # ── Chat (streaming) mode ─────────────────────────────────────────────
    if mode.startswith("💬"):
        try:
            with st.spinner("Thinking…"):
                with requests.post(
                    f"{api_url}/ask",
                    json={"query": query},
                    stream=True,
                    timeout=60,
                ) as resp:
                    resp.raise_for_status()

                    answer = ""
                    stream_box = st.empty()

                    for chunk in resp.iter_content(chunk_size=None):
                        if chunk:
                            answer += chunk.decode("utf-8", errors="replace")
                            # live update while streaming
                            stream_box.markdown(f"""
                            <div class="msg-bot">
                              <div class="msg-label">Assistant</div>
                              <div class="bubble bubble-bot">{answer} ▌</div>
                            </div>
                            """, unsafe_allow_html=True)

                    stream_box.empty()   # remove live box; history rerender will show it
                    st.session_state.messages.append({"role": "bot", "text": answer})

        except requests.exceptions.ConnectionError:
            st.session_state.messages.append({
                "role": "bot",
                "text": "❌ Cannot reach the API. Is the FastAPI server running on " + api_url + "?"
            })
        except Exception as e:
            st.session_state.messages.append({"role": "bot", "text": f"❌ Error: {e}"})

    # ── Search chunks mode ────────────────────────────────────────────────
    else:
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

            st.session_state.messages.append({"role": "bot", "text": f"📄 Retrieved chunks:\n\n{context}"})

        except requests.exceptions.ConnectionError:
            st.session_state.messages.append({
                "role": "bot",
                "text": "❌ Cannot reach the API. Is the FastAPI server running on " + api_url + "?"
            })
        except Exception as e:
            st.session_state.messages.append({"role": "bot", "text": f"❌ Error: {e}"})

    st.rerun()