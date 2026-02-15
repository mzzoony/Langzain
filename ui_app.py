# ui_app.py
import streamlit as st
from agent_core import agent_executor

st.set_page_config(page_title="Mazin's LangChain Agent", page_icon="🤖")

st.title("🤖 Mazin's LangChain + OpenAI Agent")
st.write("Ask questions, query Wikipedia, or check the weather (via tools).")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input box
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call the agent
    result = agent_executor.invoke({"input": prompt})
    answer = result["output"]

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
