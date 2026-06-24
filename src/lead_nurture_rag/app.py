from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

from .agent import LeadNurtureAgent
from .crawler import CampaignConfig, crawl_campaign
from .retriever import KnowledgeBase
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
    return {
        "company_name": req.company_name,
        "pages_crawled": len(documents),
        "chunk_ids": ids,
        "chunks_total": len(kb.chunks),
        "pages": [{"url": doc.url, "title": doc.title, "metadata": doc.metadata} for doc in documents],
    }


@app.post("/chat")
def chat(req: ChatRequest):
    history = store.get_history(req.lead_id)
    result = agent.respond(req.lead_id, history, req.message)
    store.append_turn(req.lead_id, "user", req.message)
    store.append_turn(req.lead_id, "assistant", result.reply)
    store.upsert_lead(req.lead_id, result.lead.temperature, result.lead.score, result.rationale)
    return result.model_dump(mode="json")


@app.get("/leads")
def leads():
    return store.list_leads()
