import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Trovais",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .answer-box {
        background: #f8f9fa;
        border-left: 4px solid #4361ee;
        padding: 1.2rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        color: #1a1a2e;
    }
    .source-badge {
        background: #e8f4fd;
        border: 1px solid #b8d9f5;
        border-radius: 6px;
        padding: 0.4rem 0.8rem;
        margin: 0.3rem;
        display: inline-block;
        font-size: 0.85rem;
        color: #1a6aad;
    }
    .metric-box {
        background: #f0f2f5;
        border-radius: 8px;
        padding: 0.8rem;
        text-align: center;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Trovais")
    st.markdown("*AI-powered knowledge retrieval*")
    st.divider()

    st.markdown("**Settings**")
    company_id = st.text_input("Company ID", value="demo")
    user_id = st.text_input("User ID", value="user_001")
    top_k = st.slider("Results to retrieve", 3, 10, 5)

    st.divider()
    st.markdown("**Usage this session**")
    if "query_count" not in st.session_state:
        st.session_state.query_count = 0
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Queries", st.session_state.query_count)
    with col2:
        st.metric("Tokens", st.session_state.total_tokens)

    st.divider()
    st.markdown("**Ingest a document**")
    filepath = st.text_input(
        "File path",
        placeholder="data/sample_manuals/file.pdf"
    )
    if st.button("Ingest document", use_container_width=True):
        if filepath:
            with st.spinner("Ingesting..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/api/v1/ingest",
                        json={"filepath": filepath,
                              "company_id": company_id}
                    )
                    if resp.status_code == 200:
                        st.success("Document ingested!")
                    else:
                        st.error(f"Error: {resp.json()['detail']}")
                except Exception as e:
                    st.error(f"Connection error: {e}")
        else:
            st.warning("Enter a file path first")

st.markdown(
    '<p class="main-header">Trovais</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="sub-header">'
    'Ask anything about your documents</p>',
    unsafe_allow_html=True
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message:
            st.markdown("**Sources:**")
            for source in message["sources"]:
                score = source.get("score", 0)
                if score > 0.01:
                    st.markdown(
                        f'<span class="source-badge">'
                        f'📄 {source["filename"]} '
                        f'— page {source["page"]} '
                        f'(score: {score:.2f})'
                        f'</span>',
                        unsafe_allow_html=True
                    )

if prompt := st.chat_input(
    "Ask a question about your documents..."
):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching your knowledge base..."):
            try:
                response = requests.post(
                    f"{API_URL}/api/v1/query",
                    json={
                        "question": prompt,
                        "company_id": company_id,
                        "user_id": user_id,
                        "top_k": top_k
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    sources = data["sources"]
                    tokens = data["tokens_used"]

                    st.markdown(
                        f'<div class="answer-box">{answer}</div>',
                        unsafe_allow_html=True
                    )

                    relevant_sources = [
                        s for s in sources
                        if s.get("score", 0) > 0.01
                    ]
                    if relevant_sources:
                        st.markdown("**Sources:**")
                        for source in relevant_sources:
                            st.markdown(
                                f'<span class="source-badge">'
                                f'📄 {source["filename"]} '
                                f'— page {source["page"]} '
                                f'(score: {source["score"]:.2f})'
                                f'</span>',
                                unsafe_allow_html=True
                            )

                    st.caption(f"Tokens used: {tokens}")

                    st.session_state.query_count += 1
                    st.session_state.total_tokens += tokens

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                elif response.status_code == 429:
                    st.error(response.json()["detail"])
                else:
                    st.error(
                        f"Error: {response.json().get('detail', 'Unknown error')}"
                    )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to Trovais API. "
                    "Make sure it is running on port 8000."
                )
            except Exception as e:
                st.error(f"Unexpected error: {e}")

if not st.session_state.messages:
    st.markdown("### Try asking:")
    examples = [
        "What topics are covered in this document?",
        "Explain the main concepts in chapter 1",
        "Any exercises related to palindromes?",
        "How do I work with file paths in Python?",
    ]
    cols = st.columns(2)
    for i, example in enumerate(examples):
        with cols[i % 2]:
            if st.button(example, use_container_width=True):
                st.session_state.messages.append({
                    "role": "user",
                    "content": example
                })
                st.rerun()