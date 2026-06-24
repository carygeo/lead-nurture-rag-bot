from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

from .agent import LeadNurtureAgent
from .crawler import CampaignConfig, crawl_campaign
from .observation import analyze_observation, build_observation
from .retriever import KnowledgeBase, chunk_text
from .store import ConversationStore

load_dotenv()
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
kb = KnowledgeBase(DATA_DIR / "knowledge.json")
store = ConversationStore(DATA_DIR / "leads.sqlite")
agent = LeadNurtureAgent(kb)

app = FastAPI(title="Lead Nurture RAG Bot", version="0.1.0")


class IngestTextRequest(BaseModel):
    source: str = Field(examples=["https://example.com/about"] )
    text: str


class IngestUrlRequest(BaseModel):
    url: str


class ChatRequest(BaseModel):
    lead_id: str = "demo-lead"
    message: str


@app.get("/health")
def health():
    return {"ok": True, "chunks": len(kb.chunks)}


@app.post("/ingest/text")
def ingest_text(req: IngestTextRequest):
    ids = kb.add_text(req.source, req.text)
    return {"chunk_ids": ids, "chunks_total": len(kb.chunks)}


@app.post("/ingest/url")
def ingest_url(req: IngestUrlRequest):
    ids = kb.add_url(req.url)
    return {"chunk_ids": ids, "chunks_total": len(kb.chunks)}


@app.post("/ingest/campaign")
def ingest_campaign(req: CampaignConfig):
    documents = crawl_campaign(req)
    ids = kb.add_documents(documents)
    unique_ids = list(dict.fromkeys(ids))
    chunks = [kb.chunks[chunk_id].model_dump(mode="json") for chunk_id in unique_ids if chunk_id in kb.chunks]
    return {
        "company_name": req.company_name,
        "pages_crawled": len(documents),
        "chunk_ids": ids,
        "chunks_added_or_seen": len(ids),
        "chunks_returned": len(chunks),
        "chunks_total": len(kb.chunks),
        "pages": [
            {
                "url": doc.url,
                "title": doc.title,
                "word_count": len(doc.text.split()),
                "chunk_count": len(chunk_text(doc.text)),
                "text_preview": doc.text[:500],
                "metadata": doc.metadata,
            }
            for doc in documents
        ],
        "chunks": chunks,
    }


@app.post("/chat")
def chat(req: ChatRequest):
    history = store.get_history(req.lead_id)
    result = agent.respond(req.lead_id, history, req.message)
    observation = build_observation(req.lead_id, "chat", req.message, history)
    analysis = analyze_observation(observation)
    store.append_observation(observation, analysis)
    store.append_turn(req.lead_id, "user", req.message)
    store.append_turn(req.lead_id, "assistant", result.reply)
    store.upsert_lead(req.lead_id, result.lead.temperature, result.lead.score, result.rationale)
    return result.model_dump(mode="json")


@app.get("/leads")
def leads():
    return store.list_leads()


@app.get("/leads/{lead_id}/observations")
def lead_observations(lead_id: str):
    return store.get_observations(lead_id)
