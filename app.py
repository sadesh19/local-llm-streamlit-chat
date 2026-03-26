import streamlit as st
import requests
import json

# --- Config ---
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3"  # change to whichever model you pulled

# --- Page Setup ---
st.set_page_config(page_title="Local LLM Chat", page_icon="🤖", layout="wide")
st.title("🤖 Local LLM Chat")
st.caption(f"Powered by Ollama · Model: `{MODEL_NAME}`")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Reset Button ---
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Conversation History ---
with col1:
    st.subheader("Conversation")

chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- Chat Function ---
def chat_with_ollama(messages):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": True
    }
    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            full_response = ""
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "message" in chunk:
                        token = chunk["message"].get("content", "")
                        full_response += token
                        yield token
                    if chunk.get("done"):
                        break
    except requests.exceptions.ConnectionError:
        yield "❌ Cannot connect to Ollama. Make sure it's running: `ollama serve`"
    except Exception as e:
        yield f"❌ Error: {str(e)}"

# --- Input Box ---
if prompt := st.chat_input("Ask anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Stream assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        for token in chat_with_ollama(st.session_state.messages):
            full_response += token
            response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_response})