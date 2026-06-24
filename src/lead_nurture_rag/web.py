from __future__ import annotations

import json

import requests
import streamlit as st

from lead_nurture_rag.web_helpers import (
    DEFAULT_COMPANY_URL,
    default_campaign_json,
    format_response_payload,
)

st.set_page_config(page_title="Lead nurture RAG bot", layout="wide")
API_URL = st.sidebar.text_input("API URL", "http://localhost:8000")
st.title("Lead nurture RAG bot prototype")

st.sidebar.header("Campaign crawler")
campaign_json = st.sidebar.text_area(
    "Campaign JSON",
    value=default_campaign_json(),
    height=220,
)
if st.sidebar.button("Crawl campaign website"):
    res = requests.post(f"{API_URL}/ingest/campaign", json=json.loads(campaign_json), timeout=120)
    st.sidebar.write(format_response_payload(res))

st.sidebar.header("Knowledge ingestion")
url = st.sidebar.text_input("Company URL", DEFAULT_COMPANY_URL)
if st.sidebar.button("Ingest URL") and url:
    res = requests.post(f"{API_URL}/ingest/url", json={"url": url}, timeout=60)
    st.sidebar.write(format_response_payload(res))

source = st.sidebar.text_input("Text source", "manual-company-profile")
text = st.sidebar.text_area("Paste company/site knowledge", height=180)
if st.sidebar.button("Ingest text") and text:
    res = requests.post(f"{API_URL}/ingest/text", json={"source": source, "text": text}, timeout=60)
    st.sidebar.write(format_response_payload(res))

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
