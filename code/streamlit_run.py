import streamlit as st
from main import run

st.set_page_config(page_title="Chatbot UI", page_icon="💬", layout="centered")

st.title("💬 Interactive Chatbot")

# --- Initialize chat state ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Function to handle input submission ---
def handle_message():
    user_msg = st.session_state.user_message.strip()
    if not user_msg:
        return

    # Add user message
    st.session_state.messages.append(("user", user_msg))

    # Stop condition
    if user_msg.lower() == "stop":
        bot_reply = "✅ Chat stopped. Restart to begin again."
    else:
        # Get bot response from main.py
        bot_reply = run(user_msg)

    # Add bot response
    st.session_state.messages.append(("bot", bot_reply))

    # Clear input field safely
    st.session_state.user_message = ""

# --- Chat Display ---
chat_container = st.container()
with chat_container:
    for role, text in st.session_state.messages:
        if role == "user":
            st.markdown(f"**🧑 You:** {text}")
        else:
            st.markdown(f"**🤖 Bot:** {text}")

# --- Input Field (callback triggers handle_message) ---
st.text_input(
    "Type your message (or 'stop' to end):",
    key="user_message",
    on_change=handle_message
)

# --- Clear Chat Button ---
if st.button("🧹 Clear Chat"):
    st.session_state.messages = []
    st.rerun()
