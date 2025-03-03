import streamlit as st
from dotenv import load_dotenv
from retrieval_pipeline.retriever import RetrievalPipeline

load_dotenv()

st.set_page_config(page_title="GovSeek", layout="wide")
st.title("GovSeek Chatbot")
st.subheader("Ask questions about anything found in https://www.gov.sg/trusted-sites")

pipeline = RetrievalPipeline()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving information..."):
            answer, sources, _ = pipeline.run(prompt)

        st.markdown(answer)
        sources = list(set(sources))
        if sources:
            st.subheader("Sources:")
            for source in sources:
                st.write(source)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer + "\nSources: " + ", ".join(sources),
            }
        )
