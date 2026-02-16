import sys
from pathlib import Path

# Make sure the project root is on sys.path so `import langzain...` works
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from langzain.agent_core import run_agent
from langzain.app import extract_last_assistant_message

# ---------- Page setup ----------
st.set_page_config(
    page_title="Langzain – Conversational Agent",
    page_icon="😎",
    layout="wide",
)


# Centered title + subtitle (this is what disappeared)
st.markdown(
    "<h1 style='text-align:center;'>😎 Langzain – Conversational Agent</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center;'>Ask me anything. "
    "I can chat, remember context in this session, and call tools like weather and Wikipedia.</p>",
    unsafe_allow_html=True,
)
st.write("")  # small vertical spacing


# ---------- Helper to normalize messages ----------
def get_role_and_text(msg):
    """Handle both dict messages and LangChain message objects."""
    # Role
    role = getattr(msg, "role", None)
    content = getattr(msg, "content", None)

    if isinstance(msg, dict):
        role = msg.get("role", role)
        content = msg.get("content", content)

    # Content may be plain text or a list of chunks
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(part.get("text", ""))
        text = "".join(parts) if parts else str(content)
    else:
        text = "" if content is None else str(content)

    return role, text


# ---------- Session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------- Render past conversation ----------
for msg in st.session_state.messages:
    role, text = get_role_and_text(msg)

    if role == "user":
        with st.chat_message("user", avatar="🟢"):      # green user icon
            st.markdown(text)
    elif role in ("assistant", "ai"):
        with st.chat_message("assistant", avatar="🟣"):  # purple assistant icon
            st.markdown(text)



# ---------- New user input ----------
user_input = st.chat_input("Type your message here...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # show the user's message
    with st.chat_message("user", avatar="🧑‍🎨"):
        st.markdown(user_input)

    # show assistant "thinking"
    with st.chat_message("assistant", avatar="🧠"):
        placeholder = st.empty()
        placeholder.markdown("_Thinking..._")
       
       
        updated_messages = run_agent(st.session_state.messages)
        
         # get just the latest assistant reply
        assistant_reply = extract_last_assistant_message(updated_messages)

        # 3) append assistant reply to *our* history
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_reply}
        )

        # update the bubble
        placeholder.markdown(assistant_reply)
