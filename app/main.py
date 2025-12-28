import streamlit as st
from router import router
from faq import ingest_faq_data,faq_chain
from pathlib import Path
from sql import sql_chain

faqs_path = Path(__file__).parent / "resources/faq_data.csv"
ingest_faq_data(faqs_path)

def ask(query):
    q = query.strip().lower()

    # 1️⃣ Greetings
    if q in ["hi", "hello", "hey", "hii"]:
        return "Hello! How can I help you today?"

    # 2️⃣ Route using router
    result = router(query)

    # 3️⃣ If FAQ matched → FAQ
    if result and result.name == "FAQ":
        return faq_chain(query)

    # 4️⃣ DEFAULT → SQL (MOST IMPORTANT FIX)
    return sql_chain(query)



st.title("E-commerce chatbot for flipkart")

query=st.chat_input("Write your query")

if "messages" not in st.session_state:
    st.session_state["messages"]=[]

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role":"user","content":query})

    response=ask(query)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

