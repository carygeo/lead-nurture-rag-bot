from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

LeadTemperature = Literal["cold", "warm", "hot"]


class KnowledgeChunk(BaseModel):
    id: str
    source: str
    text: str


class SearchHit(KnowledgeChunk):
    score: float = 0.0


class LeadState(BaseModel):
    lead_id: str
    temperature: LeadTemperature = "cold"
    score: int = Field(default=0, ge=0, le=100)
    signals: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentTurnResult(BaseModel):
    lead: LeadState
    reply: str
    retrieved_context: list[SearchHit]
    next_action: Literal["continue_nurture", "offer_case_study", "handoff_to_sales"]
    rationale: str
