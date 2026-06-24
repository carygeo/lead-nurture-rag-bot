from __future__ import annotations

import os
import re

from openai import OpenAI

from .models import AgentTurnResult, LeadState, SearchHit
from .retriever import KnowledgeBase

POSITIVE = {"interested", "help", "reduce", "improve", "pain", "problem", "issue", "need", "useful"}
BUYING = {"demo", "budget", "price", "pricing", "proposal", "contract", "buy", "pilot", "this week", "schedule", "book"}
OBJECTIONS = {"not interested", "too expensive", "no budget", "later", "already have", "busy", "spam"}
PAIN = {"manual", "slow", "too much time", "risk", "missing", "errors", "bottleneck", "validation"}


def _contains_any(text: str, terms: set[str]) -> list[str]:
    low = text.lower()
    return [term for term in sorted(terms) if term in low]


def score_lead(lead_id: str, history: list[str], message: str) -> LeadState:
    corpus = " ".join(history + [message]).lower()
    signals = _contains_any(corpus, POSITIVE | BUYING | PAIN)
    objections = _contains_any(corpus, OBJECTIONS)
    score = 10
    score += min(25, 6 * len(_contains_any(corpus, POSITIVE)))
    score += min(30, 8 * len(_contains_any(corpus, PAIN)))
    score += min(45, 12 * len(_contains_any(corpus, BUYING)))
    if "?" in message:
        score += 10
    if len(message.split()) > 12:
        score += 8
    score -= min(30, 10 * len(objections))
    score = max(0, min(100, score))
    temperature = "cold" if score < 40 else "warm" if score < 75 else "hot"
    return LeadState(lead_id=lead_id, temperature=temperature, score=score, signals=signals, objections=objections)


class LeadNurtureAgent:
    def __init__(self, knowledge_base: KnowledgeBase, model: str | None = None):
        self.knowledge_base = knowledge_base
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = OpenAI() if os.getenv("OPENAI_API_KEY") else None

    def respond(self, lead_id: str, history: list[str], message: str) -> AgentTurnResult:
        retrieved = self.knowledge_base.search(message, k=4)
        lead = score_lead(lead_id, history, message)
        next_action = self._next_action(lead)
        reply = self._llm_reply(lead, history, message, retrieved, next_action) if self._client else self._fallback_reply(lead, message, retrieved, next_action)
        rationale = f"{lead.temperature} lead scored {lead.score}; signals={lead.signals}; objections={lead.objections}"
        return AgentTurnResult(lead=lead, reply=reply, retrieved_context=retrieved, next_action=next_action, rationale=rationale)

    def _next_action(self, lead: LeadState) -> str:
        if lead.temperature == "hot":
            return "handoff_to_sales"
        if lead.temperature == "warm":
            return "offer_case_study"
        return "continue_nurture"

    def _llm_reply(self, lead: LeadState, history: list[str], message: str, retrieved: list[SearchHit], next_action: str) -> str:
        context = "\n\n".join(f"Source: {hit.source}\n{hit.text}" for hit in retrieved) or "No retrieved context."
        system = (
            "You are a lead nurturing chatbot prototype. Be helpful, concise, and value-led. "
            "Use retrieved company knowledge only; do not invent features. "
            "Goal: make the next conversation step slightly warmer by connecting a business pain "
            "to a concrete value point, then ask one focused qualification question. "
            "If hot, suggest a sales handoff/demo. Never pretend to be human."
        )
        user = f"Lead state: {lead.model_dump()}\nNext action: {next_action}\nHistory: {history[-6:]}\nMessage: {message}\nRetrieved context:\n{context}"
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.4,
        )
        return response.choices[0].message.content or self._fallback_reply(lead, message, retrieved, next_action)

    def _fallback_reply(self, lead: LeadState, message: str, retrieved: list[SearchHit], next_action: str) -> str:
        evidence = retrieved[0].text if retrieved else "the company knowledge base you provided"
        sentence = re.split(r"(?<=[.!?])\s+", evidence.strip())[0][:240]
        if next_action == "handoff_to_sales":
            return (
                f"Based on what you shared, this sounds like an active fit. {sentence} "
                "A practical next step would be a short workflow review with someone who can map it to your project. "
                "What day this week would be easiest for a 20-minute demo?"
            )
        if next_action == "offer_case_study":
            return (
                f"That pain is exactly where the strongest value tends to show up: {sentence} "
                "If useful, I can walk through a quick example of how this would reduce review effort. "
                "Which part of the workflow is most painful right now?"
            )
        return (
            f"A useful starting point is this: {sentence} "
            "The goal would be to reduce low-value manual follow-up before asking you for more time. "
            "What workflow or outcome would make this worth exploring for your team?"
        )
