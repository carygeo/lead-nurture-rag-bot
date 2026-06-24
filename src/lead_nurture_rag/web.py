from __future__ import annotations

import requests
import streamlit as st

API_URL = st.sidebar.text_input("API URL", "http://localhost:8000")
st.set_page_config(page_title="Lead nurture RAG bot", layout="wide")
st.title("Lead nurture RAG bot prototype")

st.sidebar.header("Campaign crawler")
campaign_json = st.sidebar.text_area(
    "Campaign JSON",
    value='''{
  "company_name": "Example Construction AI",
  "root_url": "https://example.com",
  "allowed_domains": ["example.com"],
  "seed_pages": ["https://example.com/"],
  "crawl_depth": 1,
  "max_pages": 25,
  "target_persona": "construction project executive",
  "offer": "AI payment application validation workflow"
}''',
    height=220,
)
if st.sidebar.button("Crawl campaign website"):
    res = requests.post(f"{API_URL}/ingest/campaign", json=__import__("json").loads(campaign_json), timeout=120)
    st.sidebar.write(res.json())

st.sidebar.header("Knowledge ingestion")
url = st.sidebar.text_input("Company URL")
if st.sidebar.button("Ingest URL") and url:
    res = requests.post(f"{API_URL}/ingest/url", json={"url": url}, timeout=60)
    st.sidebar.write(res.json())

source = st.sidebar.text_input("Text source", "manual-company-profile")
text = st.sidebar.text_area("Paste company/site knowledge", height=180)
if st.sidebar.button("Ingest text") and text:
    res = requests.post(f"{API_URL}/ingest/text", json={"source": source, "text": text}, timeout=60)
    st.sidebar.write(res.json())

lead_id = st.text_input("Lead ID", "demo-lead")
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Write as the potential lead..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    res = requests.post(f"{API_URL}/chat", json={"lead_id": lead_id, "message": prompt}, timeout=60)
    data = res.json()
    reply = data["reply"]
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
    c1, c2, c3 = st.columns(3)
    c1.metric("Temperature", data["lead"]["temperature"])
    c2.metric("Score", data["lead"]["score"])
    c3.metric("Next action", data["next_action"])
    with st.expander("Retrieved context / rationale"):
        st.write(data["rationale"])
        st.json(data["retrieved_context"])
