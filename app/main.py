import streamlit as st
from pathlib import Path

from router import router
from faq import ingest_faq_data, faq_chain
from sql import sql_chain

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="E-commerce Chatbot",
    page_icon="🛒",
    layout="centered"
)

# ==================================================
# LOAD FAQ DATA (RUN ONCE)
# ==================================================
faqs_path = Path(__file__).parent / "resources/faq_data.csv"

@st.cache_resource
def load_faq_data():
    ingest_faq_data(faqs_path)

load_faq_data()

# ==================================================
# CORE LOGIC
# ==================================================
def ask(query: str) -> str:
    q = query.strip().lower()

    # 1️⃣ Greetings
    if q in {"hi", "hello", "hey", "hii"}:
        return "Hello! How can I help you today?"

    # 2️⃣ Semantic routing
    result = router(query)

    # 3️⃣ FAQ route
    if result and result.name == "FAQ":
        return faq_chain(query)

    # 4️⃣ Default → SQL
    return sql_chain(query)

# ==================================================
# UI
# ==================================================
st.title("🛍️ E-commerce Chatbot for Flipkart")

# Clear chat button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🧹 Clear") and "messages" in st.session_state:
        st.session_state.messages = []
        st.rerun()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
query = st.chat_input("Write your query")

# ==================================================
# HANDLE USER INPUT
# ==================================================
if query:
    # Show user message
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append(
        {"role": "user", "content": query}
    )

    # Spinner during LLM work
    with st.spinner("Thinking... 🤖"):
        response = ask(query)

    # Show assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
