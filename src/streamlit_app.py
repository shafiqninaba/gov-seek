import streamlit as st
from dotenv import load_dotenv
from retrieval_pipeline.retriever import RetrievalPipeline
from uuid import uuid4

load_dotenv()

st.set_page_config(page_title="GovSeek", layout="wide")
st.title("GovSeek Chatbot")
st.subheader("Ask questions about anything found in https://www.gov.sg/trusted-sites")

if "thread_id" not in st.session_state:
    st.session_state.pipeline = RetrievalPipeline()
    st.session_state.thread_id = str(uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message:
            sources = message["sources"]
            if sources:
                st.subheader("Sources:")
                for source in sources:
                    st.write(source)

if prompt := st.chat_input("Ask me anything"):
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate assistant response
    with st.spinner("Retrieving relevant information..."):
        answer, sources = st.session_state.pipeline.run(
            prompt, st.session_state.thread_id
        )

    # Add assistant response to session state with sources
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": list(set(sources)) if sources else [],
        }
    )

    # Force a rerun to display the new messages
    st.rerun()
