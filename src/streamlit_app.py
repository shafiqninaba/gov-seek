"""Streamlit app for the GovSeek chatbot."""

import streamlit as st
from dotenv import load_dotenv
from retrieval_pipeline.retriever import RetrievalPipeline
from uuid import uuid4
import hashlib

load_dotenv()

st.set_page_config(page_title="GovSeek", layout="wide")

# GitHub link
GITHUB_URL = "https://github.com/shafiqninaba/gov-seek"
LINKEDIN_URL = "https://www.linkedin.com/in/shafiq-ninaba"

# Define the password
CORRECT_PASSWORD = "14128ce9d7573671f28e95987d19bd40"

# Initialize authentication state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


# Footer function
def display_footer():
    """Display the footer with GitHub and LinkedIn links."""
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center;">
            <a href="{}" target="_blank">
                <img src="https://img.icons8.com/fluent/48/000000/github.png" alt="GitHub" width="30"/>
            </a>
            <a href="{}" target="_blank">
                <img src="https://img.icons8.com/fluent/48/000000/linkedin.png" alt="LinkedIn" width="30"/>
            </a>
        </div>
        """.format(GITHUB_URL, LINKEDIN_URL),
        unsafe_allow_html=True,
    )


# Authentication section
if not st.session_state.authenticated:
    st.title("GovSeek - Login Required")

    # Simple password form
    with st.form("login_form"):
        password = st.text_input("Enter Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if hashlib.md5(str.encode(password)).hexdigest() == CORRECT_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")
    display_footer()

# Main app - only shown if authenticated
else:
    st.title("GovSeek Chatbot")
    st.subheader(
        "Ask questions about anything found in https://www.gov.sg/trusted-sites"
    )

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
                        st.markdown(f"- {source}")

    if prompt := st.chat_input("Ask me anything"):
        # Display user message immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Retrieving relevant information..."):
            answer, sources = st.session_state.pipeline.run(
                prompt, st.session_state.thread_id
            )
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources if sources else None,
            }
        )

        st.rerun()

    display_footer()
